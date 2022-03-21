from decouple import config
from py5paisa import FivePaisaClient
import time
import json
from datetime import date, datetime
import csv

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

if market_depth: 
    previous_day_close = market_depth['Data'][0]['Close']
    previous_day_high = market_depth['Data'][0]['High']
    previous_day_low = market_depth['Data'][0]['Low']
    # print(previous_day_high, previous_day_low)

print('Your API fetching took', time.time() - t1, 's to execute')

# Live Feed
req_list_for_live_feed = [
            { 
                "Exch":"N",
                "ExchType":"C",
                "ScripCode":scripcode
            },            
]

# Flag for first 10 mins
flag_first_10_min = False
# first_10_mins = datetime.time(9, 26, 0)
dict = client.Request_Feed('mf', 's', req_list_for_live_feed)
first_10_mins_high = None
first_10_mins_low = None

trade_taken = True
trade = {}

# Backtest Data File CSV 
backtest_data_file = open(f'./Golden_Ratio_Backtest/{stock_name}_Intraday_Backtest_Results_Golden_Ratio.csv')
backtest_data = csv.DictReader(backtest_data_file)

new_backtest_data = []
for row in backtest_data:
    new_backtest_data.append(row)

def on_message(ws, message):
    
    # print("hi")
    print(message)
    now = datetime.now()
    json_data = json.loads(message)
    # print(now.hour)
    
    if now.hour > 15 or now.hour < 9 or (now.hour == 15 and now.minute >= 20) or (now.hour == 9 and now.minute <= 15):
        
        if trade_taken:
            trade['exit_price'] = json_data[0]['PClose']
            trade['pnl'] = trade['exit_price'] - trade['entry_price']
            trade['success'] = trade['pnl'] > 0
            trade['trade_exit_time'] = datetime.now()
            trade_taken = False
            new_backtest_data.append(trade)
        
        backtest_data_file = open(f'./Golden_Ratio_Backtest/{stock_name}_Intraday_Backtest_Results_Golden_Ratio.csv', 'w', newline='')
        data_list = csv.DictWriter(backtest_data_file, fieldnames = [
            'trade_time', 
            'entry_price', 
            'stop_loss', 
            'target', 
            'exit_price', 
            'trade_exit_time', 
            'trade_type', 
            'pnl', 
            'success', 
            'pnl',
        ])
    
        data_list.writeheader()
        data_list.writerows(new_backtest_data)
        # sys.exit()
        
    if (not flag_first_10_min) and now.hour == 9 and now.minute == 26:
        flag_first_10_min = True
        first_10_mins_high = json_data[0]['High']
        first_10_mins_high = json_data[0]['Low']
        
    if flag_first_10_min:
        if trade_taken: 
            if trade['trade_type'] == 'long' and (trade['stop_loss'] >= json_data[0]['PClose'] or trade['target'] <= json_data[0]['PClose']):
                    trade['exit_price'] = json_data[0]['PClose']
                    trade['pnl'] = trade['exit_price'] - trade['entry_price']
                    trade['success'] = trade['pnl'] > 0
                    trade['trade_exit_time'] = datetime.now()
                    trade_taken = False
                    new_backtest_data.append(trade)
                                        
            elif trade['trade_type'] == 'short' and (trade['stop_loss'] <= json_data[0]['PClose'] or trade['target'] >= json_data[0]['PClose']):
                    trade['exit_price'] = json_data[0]['PClose']
                    trade['pnl'] = trade['exit_price'] - trade['entry_price']
                    trade['success'] = trade['pnl'] > 0
                    trade['trade_exit_time'] = datetime.now()
                    trade_taken = False
                    new_backtest_data.append(trade)
            
        else:
            if json_data[0]['PClose'] > first_10_mins_high:
                trade = {
                    "trade_time": datetime.now(),
                    "entry_price": json_data[0]['PClose'],
                    "stop_loss": json_data[0]['PClose'] * 0.995,
                    "target": json_data[0]['PClose'] * 0.102,
                    "trade_type": "long"
                } 
                
                trade_taken = True  
                  
            elif json_data[0]['PClose'] < first_10_mins_low:
                trade = {
                    "trade_time": datetime.now(),
                    "entry_price": json_data[0]['PClose'],
                    "stop_loss": json_data[0]['PClose'] * 0.1005,
                    "target": json_data[0]['PClose'] * 0.98,
                    "trade_type": "short"
                }     
                
                trade_taken = True
                

client.connect(dict)
client.receive_data(on_message)