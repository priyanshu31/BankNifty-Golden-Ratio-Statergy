from telnetlib import AUTHENTICATION
from click import confirmation_option
from nsepython import *
from decouple import config
from py5paisa import FivePaisaClient
import pandas
import time
import json
import os

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

# Previous Day's High
# Previous Day's Low
# Opening 10 mins Range