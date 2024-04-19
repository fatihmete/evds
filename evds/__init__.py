import pandas as pd
import requests
import json
import ssl
import urllib3

class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


class evdsAPI:
    """
    for more detail https://github.com/fatihmete/evds
    Example usage:
    from evds import evdsAPI
    evds = evdsAPI('EVDS_API_KEY')
    evds.get_data(['TP.DK.USD.A.YTL','TP.DK.EUR.A.YTL'], startdate="01-01-2019", enddate="01-01-2020")
    """

    def __init__(self, key, lang="TR", DEBUG=False, proxies="", httpsVerify=True, legacySSL=True):
        self.key = key
        self.DEBUG = DEBUG
        self.proxies = proxies
        self.httpsVerify = httpsVerify
        self.legacySSL = legacySSL

        self.__create_session()

        if lang in ["TR", "ENG"]:
            self.lang = lang
        else:
            self.lang = "TR"
        # API returns this main categories but they are not available
        self.not_available_categories = [17]

        self.main_categories = self.__get_main_categories()

    def __create_session(self):
        self.session = requests.Session()
        if self.legacySSL:
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
            self.session.mount('https://', CustomHttpAdapter(ctx))

        if self.proxies != "":
            self.session.proxies = self.proxies
            self.session.verify = self.httpsVerify

    def __get_main_categories(self):
        """
        Function returns main categories dataframe.
        """
        main_categories = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/categories/',
                                              params={'type': 'json'})
        try:
            main_categories_raw = json.loads(main_categories)
            main_categories_df = pd.DataFrame(main_categories_raw)[
                ["CATEGORY_ID", "TOPIC_TITLE_" + self.lang]]
            main_categories_df["CATEGORY_ID"] = main_categories_df["CATEGORY_ID"].astype(
                "int")
            return main_categories_df[~main_categories_df.CATEGORY_ID.isin(self.not_available_categories)]

        except:
            raise EVDSConnectionError(
                f"Main categories couldn't load. Please check your API Key.")

    def get_sub_categories(self, main_category="", detail=False, raw=False):
        """
        The function returns sub-categories as dataframe object.
        If main_category,
            - Not defined, returns all subcategories,
            - Defined as an integer, returns subcategories which main category id match this value,
            - Defined as a string, depending on self.lang value, search in main category name and 
              returns matched the main category' subcategories
        """
        if main_category == "":
            params = {'mode': 0, 'code': '', 'type': 'json'}

        elif isinstance(main_category, (int, float)):
            if main_category in self.main_categories["CATEGORY_ID"].to_list():
                params = {'mode': 2, 'code': main_category, 'type': 'json'}
            else:
                raise CategoryNotFoundError("Category not found.")
        else:
            try:
                code = self.main_categories[self.main_categories["TOPIC_TITLE_" +
                                                                 self.lang].str.contains(main_category)]["CATEGORY_ID"].values[0]
                params = {'mode': 2, 'code': code, 'type': 'json'}
            except:
                raise CategoryNotFoundError("Category not found.")

        sub_categories = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/datagroups/',
                                             params=params)
        sub_categories = json.loads(sub_categories)
        if raw:
            return sub_categories
        df = pd.DataFrame(sub_categories)
        if detail == False:
            return df[["CATEGORY_ID",
                       "DATAGROUP_CODE",
                       "DATAGROUP_NAME" + ("_ENG" if self.lang == "ENG" else "")]]

        return df

    def get_series(self, datagroup_code, detail=False, raw=False):
        """
        The function returns dataframe of series which belongs to given data group.
        Because of default detail parameter is False, only return "SERIE_CODE", "SERIE_NAME" and "START_DATE" value.
        """
        series = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/serieList/',
                                     params={'type': 'json', 'code': datagroup_code})
        series = json.loads(series)
        if raw:
            return series
        df = pd.DataFrame(series)
        if detail == False:
            return df[["SERIE_CODE",
                       "SERIE_NAME" + ("_ENG" if self.lang == "ENG" else ""),
                       "START_DATE"]]

        return df

    def get_data(self, series, startdate, enddate="", aggregation_types="", formulas="", frequency="", raw=False):
        """
        The function returns data of the given series data. Series must be typed as list.
        Also, set parameter raw=False to return dictionary format.
        If end date not defined, end date set as equal to start date
        If aggregation_types and formulas,
            - not defined, API returns value aggregated and calculated default aggregations type and formula for the series.
            - defined as a string, given aggregation type and formula applied for all given series
            - defined as a list, given aggregation types and formulas applied for given series respectively.
        Available aggregation types are avg, min, max, first, last, sum.
        Available formulas are the following:
            Percentage change: 1
            Difference: 2
            Yearly percentage change: 3
            Yearly difference: 4
            Percentage change in comparison with end of previous year: 5
            Difference in comparison with end of previous year: 6
            Moving average: 7
            Moving total: 8
        It is possible to set frequency of data. Possible frequencies are the following:
            Daily: 1
            Workday: 2
            Weekly: 3
            Two times in a month: 4
            Monthly: 5
            Quarterly: 6
            Six month: 7
            Yearly: 8
        """
        if isinstance(series, list) == False:
            return print("Series type must be list.")

        # For daily data set enddate to startdate, if blank
        if enddate == "":
            enddate = startdate

        series_count = len(series)

        # Set aggregation type
        if aggregation_types == "":
            # Default aggregation method
            aggregation_type_param = ''
        elif isinstance(aggregation_types, list):
            # User defined aggregation per series
            aggregation_type_param = "-".join([str(i)
                                              for i in aggregation_types])
        else:
            # User defined aggregation same for all series
            aggregation_type_param = "-".join([str(aggregation_types)
                                              for i in range(series_count)])

        # Set formulas
        if formulas == "":
            # Default formula
            formula_param = ''
        elif isinstance(formulas, list):
            # User defined formula per series
            formula_param = "-".join([str(i) for i in formulas])
        else:
            # User defined formula same for all series
            formula_param = "-".join([str(formulas)
                                     for i in range(series_count)])

        data = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/',
                                   params={
                                       'series': "-".join(series),
                                       'startDate': startdate,
                                       'endDate': enddate,
                                       'type': 'json',
                                       'formulas': formula_param,
                                       'frequency': str(frequency),
                                       'aggregationTypes': aggregation_type_param,
                                   })
        data = json.loads(data)["items"]
        # If raw is true return only json results.
        if raw:
            return data

        df = pd.DataFrame(data)

        # Numeric values in json data is defined as string. To fix this problem, we cast values to float.
        for serie_col in [s.replace(".", "_") for s in series]:
            if serie_col in df.columns:
                df[serie_col] = df[serie_col].astype("float")

        if "UNIXTIME" in df.columns:
            df.drop(columns=["UNIXTIME"], inplace=True)
        return df

    def __make_request(self, url, params={}):
        params = self.__param_generator(params)
        request = self.session.get(url + params, headers={'key': self.key})
        self.session.close()
        print(request.url) if self.DEBUG == True else None
        if request.status_code == 200:
            return request.content
        else:
            raise EVDSConnectionError(
                "Connection error, please check your API Key or request. Url:{}".format(request.url))

    def __param_generator(self, param):
        param_text = ''
        for key, value in param.items():
            param_text += str(key) + "=" + str(value)
            param_text += '&'
        return param_text[:-1]


class CategoryNotFoundError(Exception):
    pass


class EVDSConnectionError(Exception):
    pass
