import unittest
import warnings
from unittest.mock import patch

from evds import evdsAPI


class MockSession:
    def __init__(self, json_data, status_code, content, url):
        self.json_data = json_data
        self.status_code = status_code
        self.content = content
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # session.close()
        return self

    def get(self, *args):
        self.url = args[0]
        if args[0] == 'https://evds2.tcmb.gov.tr/service/evds/categories/key=APIKEY&type=json':
            self.json_data = b'{"key1": "value1"}'
            self.status_code = 200
            self.content = b'{"CATEGORY_ID": [2], "TOPIC_TITLE_TR": [3]}'
        elif args[0] == 'https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.USD.A.YTL-TP.DK.EUR.A.YTL&startDate=01-03-2019&endDate=01-03-2019&type=json&key=APIKEY&formulas=&frequency=&aggregationTypes=':
            self.json_data = b'{"key1": "value1"}'
            self.status_code = 200
            self.content = b'{"items": {"Tarih": ["01-03-2019"], "TP_DK_USD_A_YTL": ["5.3177"], "TP_DK_EUR_A_YTL": ["6.0576"]}}'
        else:
            self.json_data = None
            self.status_code = 404
            self.content = None

        return self

    def json(self):
        return self.json_data


class EVDSTest(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter(action='ignore', category=FutureWarning)

    @patch('requests.Session')
    def test_get_data(self, mock_session):
        mock_session.return_value = MockSession('', 404, '', '')
        self.evds = evdsAPI('APIKEY')
        data = self.evds.get_data(['TP.DK.USD.A.YTL', 'TP.DK.EUR.A.YTL'], startdate="01-03-2019")

        self.assertEqual(data.at[0, 'Tarih'], '01-03-2019')
        self.assertEqual(data.at[0, 'TP_DK_USD_A_YTL'], 5.3177)


if __name__ == '__main__':
    unittest.main()