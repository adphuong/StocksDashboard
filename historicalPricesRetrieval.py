from bs4 import BeautifulSoup
from datetime import *
from flask import Flask, request
import requests
import json
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

app = Flask(__name__)


@app.route("/")
def response():
    ticker = request.args['stock']
    start = datetime.strptime(request.args['start'], "%Y-%m-%d")
    end = datetime.strptime(request.args['end'], "%Y-%m-%d")
    return get_info(start, end, ticker)


def date_converter(date):
    difference = date - datetime(1993, 10, 25, 12, 0, 0)
    seconds = difference.total_seconds()
    return int(seconds + 751593600)


def scrape(start_date, end_date, stock_ticker):
    url = 'https://finance.yahoo.com/quote/' + stock_ticker + '/history?period1=' + start_date + '&period2=' + end_date
    source = requests.get(url, headers=headers).text
    soup = BeautifulSoup(source, features="html.parser")
    table = soup.find('tbody')
    info = {}
    for i in range(len(table.contents)):
        info[i] = \
            [table.contents[i].contents[0].contents[0].contents[0],
            table.contents[i].contents[1].contents[0].contents[0],
            table.contents[i].contents[4].contents[0].contents[0]]

    return info


def get_info(start, end, stock_ticker):
    current = date_converter(end)
    end = date_converter(start)
    info = {}
    while current != end:
        new_current = max(end, current - 30 * 5 * 86400)
        current_dict = scrape(str(new_current), str(current), stock_ticker)
        info.update(current_dict)
        current = new_current
    return json.dumps(info)

app.run("127.0.0.1", 3500)
