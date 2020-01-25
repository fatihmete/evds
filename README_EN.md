# EVDS
EVDS package allows you to access statistical data released by Central Bank of the Republic of Turkey (CBRT) (Electronic Data Delivery System (EDDS)) with Python.

With the EVDS package, you can access all the following data:
- MARKET STATISTICS
- EXCHANGE RATES
- INTEREST RATES
- MONEY AND BANKING STATISTICS
- WEEKLY SECURITIES STATISTICS
- FINANCIAL STATISTICS
- CBRT BALANCE SHEET DATA
- PRICE INDICES
- SURVEYS
- BALANCE OF PAYMENTS INTERNATIONAL INVESTMENT P...
- FOREIGN TRADE STATISTICS
- PUBLIC FINANCE
- PRODUCTION STATISTICS
- PAYMENT SYSTEMS AND EMISSION
- EMPLOYMENT STATISTICS
- EXTERNAL DEBT
- GOLD STATISTICS
- HOUSING AND CONSTRUCTION STATISTICS
- TOURISM STATISTICS

## Installation
```
pip install evds --upgrade
```
## Usage
```python
from evds import evdsAPI
evds = evdsAPI('EVDS_API_KEY', lang="ENG")
evds.get_data(['TP.DK.USD.A.YTL','TP.DK.EUR.A.YTL'], startdate="01-01-2019", enddate="01-01-2020")
```
### Get API Key
To use the evds package, you must first get the API Key on the EVDS system. To get the API Key, follow the steps below:
1. Open [EVDS](https://evds2.tcmb.gov.tr/) page and create an EVDS Account.
2. Then click on the profile link under your username.

![01](01.png)

3. Click the "API Key" button at the bottom of your profile page and copy the value in the box that opens.

![02](02.png)
