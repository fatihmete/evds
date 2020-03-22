import pandas as pd
import requests
import json

class evdsAPI:
    """
    for more detail https://github.com/fatihmete/evds
    Example usage:
    from evds import evdsAPI
    evds = evdsAPI('EVDS_API_KEY')
    evds.get_data(['TP.DK.USD.A.YTL','TP.DK.EUR.A.YTL'], startdate="01-01-2019", enddate="01-01-2020")
    """
    def __init__(self, key, lang = "TR", DEBUG=False, proxies = "", httpsVerify = True):
        self.key = key
        self.DEBUG = DEBUG
        self.proxies = proxies
        self.httspVerify = httpsVerify
        self.session = requests.Session()
        if self.proxies != "":
            self.session.proxies = self.proxies
            self.session.verify = self.httspVerify
        
        if lang in ["TR","ENG"]:
            self.lang = lang
        else:
            self.lang = "TR"

        #All categories in EVDS not accesible via API. So we use only available categories. This issue fixed by update.
        #self.available_categories = [13, 18, 21,  1,  4, 15, 22,  6,  2, 19,  0, 12, 14, 26, 20,  3, 25, 23,  5, 28]

        self.main_categories = self.__get_main_categories()

    def __get_main_categories(self, raw=False):
        """
        Function returns main categories dataframe.
        """
        main_categories = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/categories/',\
                            params={'key' : self.key, 'type' : 'json'})
        try:
            self.main_categories_raw = json.loads(main_categories)
            main_categories_df = pd.DataFrame(self.main_categories_raw, dtype="int")[["CATEGORY_ID","TOPIC_TITLE_" + self.lang]]
            # return main_categories_df[main_categories_df.CATEGORY_ID.isin(self.available_categories)] Fixed
            return main_categories_df
        except:
            return print("Main categories couldn't load. Please check your API Key.")

    def get_sub_categories(self, main_category="", detail=False):
        """
        The function returns sub-categories as dataframe object.
        If main_category,
            - Not defined, returns all subcategories,
            - Defined as an integer, returns subcategories which main category id match this value,
            - Defined as a string, depending on self.lang value, search in main category name and 
              returns matched the main category' subcategories
        """
        if main_category == "":
            params={ 'key' : self.key, 'mode' : 0, 'code' : '', 'type' : 'json'}
            
        elif isinstance(main_category, (int,float)):
            params={ 'key' : self.key, 'mode' : 2, 'code' : main_category, 'type' : 'json'}

        else:
            try:
                code = self.main_categories[self.main_categories["TOPIC_TITLE_"+self.lang].str.contains(main_category)]\
                        ["CATEGORY_ID"].values[0]
                params={ 'key' : self.key, 'mode' : 2, 'code' : code , 'type' : 'json'}
            except:
                print("Category not found.")
                params={ 'key' : self.key, 'mode' : 0, 'code' : '', 'type' : 'json'}

        sub_categories = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/datagroups/',\
                            params=params)
        self.sub_categories = pd.DataFrame(json.loads(sub_categories))

        if detail==False:
            return self.sub_categories[["CATEGORY_ID",\
                                        "DATAGROUP_CODE",\
                                        "DATAGROUP_NAME" + ("_ENG" if self.lang=="ENG" else "")]]
        else:
            return self.sub_categories

    def get_series(self, datagroup_code, detail=False):
        """
        The function returns dataframe of series which belongs to given data group.
        Because of default detail parameter is False, only return "SERIE_CODE", "SERIE_NAME" and "START_DATE" value.
        """
        series = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/serieList/',\
                                    params = {'key' : self.key, 'type' : 'json', 'code' : datagroup_code})
        self.series_df = pd.DataFrame(json.loads(series))
        if detail == False:
            return self.series_df[["SERIE_CODE",\
                                "SERIE_NAME" + ("_ENG" if self.lang=="ENG" else ""),\
                                "START_DATE"]]
        else:
            return self.series_df
        
    def get_data(self, series, startdate, enddate="", aggregation_types="", formulas="", frequency=""):
        """
        The function returns data of the given series data. Series must be typed as list.
        Also, set self.data variable which contains raw (JSON) value of series value.
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
        if isinstance(series, list)==False:
            return print("Series type must be list.")
            
        #For daily data set enddate to startdate, if blank
        if enddate=="":
            enddate = startdate
            
        series_count = len(series)
        
        #Set aggregation type
        if aggregation_types=="":
            #Default aggregation method
            aggregation_type_param = ''
        elif isinstance(aggregation_types, list):
            #User defined aggregation per series
            aggregation_type_param = "-".join([i for i in aggregation_types])
        else:
            #User defined aggregation same for all series
            aggregation_type_param = "-".join([aggregation_types for i in range(series_count)])

        #Set formulas
        if formulas=="":
            #Default formula
            formula_param = ''
        elif isinstance(formulas, list):
            #User defined formula per series
            formula_param = "-".join([i for i in formulas])
        else:
            #User defined formula same for all series
            formula_param = "-".join([formulas for i in range(series_count)])

        data = self.__make_request('https://evds2.tcmb.gov.tr/service/evds/',\
                           params = {
                            'series' : "-".join(series),
                            'startDate' : startdate,
                            'endDate' : enddate,
                            'type' : 'json',
                            'key' : self.key,
                            'formula' : formula_param,
                            'frequency' : str(frequency),
                            'aggregationTypes' : aggregation_type_param,

                            })
        self.data = json.loads(data)["items"]
        try:
            #Numeric values in json data is defined as text. To fix this problem, set dtype="float"
            return pd.DataFrame(self.data, dtype="float").drop(columns=["UNIXTIME"]) #.iloc[:,:-1]
        except:
            return pd.DataFrame(self.data, dtype="float")

    def __make_request(self,url,params={}):
        params = self.__param_generator(params)
        
        request = self.session.get(url + params)
        print(request.url) if self.DEBUG==True else None
        if request.status_code==200:

            return request.content
        else:
            print("Connection error, Url:{}".format(request.url))
            return None

    def __param_generator(self,param):
        param_text = ''
        for key,value in param.items():
            param_text += str(key) + "=" + str(value)
            param_text += '&'
        return param_text[:-1]
