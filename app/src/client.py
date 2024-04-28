import os
polygonKey = os.environ.get("POLYGON_API_KEY")

import datetime
import holidays
import json
from polygon import RESTClient
import redis
import requests

def is_business_day(date):
    # Check if the day is a weekday (Monday=0, Sunday=6)
    if date.weekday() < 5:
        # Check if the day is not a public holiday
        if date not in holidays.CountryHoliday('USA'):
            return True
    return False

def last_business_day(date):
    prev_day = date - datetime.timedelta(days=1)
    while not is_business_day(prev_day):
        prev_day -= datetime.timedelta(days=1)
    return prev_day

today = datetime.date.today()

if is_business_day(today):
    day = today.strftime('%Y-%m-%d')
else:
    last_bd = last_business_day(today)
    day = last_bd.strftime('%Y-%m-%d')

# Here we get the API_KEY that was saved in the environment variable
redis_conn = redis.StrictRedis(
    host='localhost', 
    port=6379,
    decode_responses=True,
    db=0
)

def getQuote(ticker):
    response = requests.get(f"https://api.polygon.io/v1/open-close/{ticker}/{day}?apiKey={polygonKey}")
    if response.status_code == 200:
        data = response.json()
        try:
            redis_conn.set(ticker, json.dumps(data), ex=30)
        except Exception as e:
            print(e)
        redis_conn.setex(ticker, 5*24*60*60, json.dumps(data))
        print(data)
        return data
    else:
        print(response.status_code)
        print(response.text)
        return None

def getTickers(ticker):
    response = requests.get(f"https://api.polygon.io/v1/reference/tickers?market='stocks'&apiKey{day}?apiKey={polygonKey}")
    if response.status_code == 200:
        data = response.json()
        try:
#second way to get data:
"""
def getQuote(ticker):
    client = RESTClient(api_key=polygonKey)
    quote = client.get_daily_open_close_agg(ticker, day)
    redis_conn.set(ticker, json.dumps(quote), ex=30)
    print(quote)
    return quote
"""

#For my test
getQuote("AAPL")