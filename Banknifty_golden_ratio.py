from telnetlib import AUTHENTICATION
from click import confirmation_option
from nsepython import *
from decouple import config
from py5paisa import FivePaisaClient
import pandas
import time
import json
import os

t1 = time.time()

# Loading data from env
email = config('5PAISA_EMAIL')
pwd = config('5PAISA_PASSWORD')
dob = config('5PAISA_DOB')
app_name = config("APP_NAME")
app_source = config("APP_SOURCE")
user_id = config("USER_ID")
password = config("PASSWORD")
user_key = config("USER_KEY")
encryption_key = config("ENCRYPTION_KEY")

# Intializing object credentials
cred = {
    "APP_NAME" : app_name,
    "APP_SOURCE" : app_source,
    "USER_ID" : user_id,
    "PASSWORD" : password,
    "USER_KEY" : user_key,
    "ENCRYPTION_KEY" : encryption_key
}

# 5paisa Authentication
client = FivePaisaClient(email=email, passwd=pwd, dob=dob,cred=cred)
client.login()

print("Your Authentication took ", time.time() - t1, 's to execute')
t1 = time.time()

# scripcode loading #

json_scripcode_file = open('./ScripCodes/new-scripcode-json.json')
json_scripcode_data = json.load(json_scripcode_file)

stock_name = 'BANKNIFTY'
scripcode = json_scripcode_data[stock_name]['Scripcode']

# scripcode loading #

# Data Fetching and Storing #

# df=pandas.DataFrame(client.historical_data('N','C',scripcode,'1m','2022-02-22','2022-02-22'))
# print(df)
# df.to_csv(f"./{stock_name}_fetched_data.csv")

# Data Fetching and Storing #

# MARKET FEED
req_list = [
            { 
                "Exchange":"N",
                "ExchangeType":"C",
                "ScripCode":scripcode
            },            
]

# Previous Day's High
# Previous Day's Low

market_depth = client.fetch_market_depth(req_list)
# print(market_depth)
previous_day_high = market_depth['Data'][0]['High']
previous_day_low = market_depth['Data'][0]['Low']
# print(previous_day_high, previous_day_low)

print('Your API fetching took', time.time() - t1, 's to execute')

# Opening 10 mins Range