from bs4 import BeautifulSoup
import requests
import csv
import re
import operator
from collections import OrderedDict
import json
import datetime

# Get mutual fund value from google:
# https://www.google.com/finance?q=MUTF_IN%3AAXIS_LT_EQUI_1RWJOWW&ei=mvjqWLDVCJOHuQSrmb2ABw

ids = ["f00000sc5y",    # DSP BlackRock Micro Cap Dir Gr
       "f00000pd2b",    # Mirae Asset Emerging Bluechip Dir Gr
       "f00000pdsi",    # Canara Robeco Emerging Equities Dir Gr
       ]

# proxyDict = {
#     "http": http_proxy,
#     "https": http_proxy,
#     "ftp": http_proxy
# }

proxyDict = None

try:
    result = requests.get("http://google.com", proxies=proxyDict, timeout=5)
except:
    proxyDict = None

# Add fund with appropriate category in json
with open('funds.json') as data_file:
    data = json.load(data_file)


def remove_words(query):
    stopwords = ["ltd", "limited"]
    querywords = query.split()
    resultwords = [word for word in querywords if word.lower() not in stopwords]
    result = ' '.join(resultwords)
    result = re.sub(r'([^\w\s]|_)+(?=\s|$)', '', result)
    return result

def slugify(string):
    return re.sub(r'[-\s]+', '-', (re.sub(r'[^\w\s-]', '', string).strip().lower()))

def getPriceOfEachStock(name):
    change=0
    url="http://www.morningstar.in"+name
    result = requests.get(url,proxies=proxyDict,timeout=30)
    if result.status_code == 200:
        soup1 = BeautifulSoup(result.content, "lxml")
        change=soup1.find("div", attrs={"vkey": "DayChange"}).find_all('span')[2].get_text().strip()
    return change

datasets = []
total_weight=0
changed_weight=0


def get_change_in_mf():
    global total_weight, changed_weight
    change=0
    try:
        stock_url = row.find_all('a', href=True)[0]['href']
        change = float(getPriceOfEachStock(stock_url))
        print('Change for {0} is {1}'.format(temp[0], change))
    except IndexError:
        change = 0
        print('We couldnt find url for ', temp[0])
    except ValueError:
        print('We couldnt find price change for ', temp[0])
        change = 0
    weight = float(temp[3])
    total_weight = total_weight + weight
    changed_weight = changed_weight + weight + ((weight / 100) * change)


for id in [key['key'] for key in data['funds']['mid']]:
    #      http://www.morningstar.in/mutualfunds/f00000tgku/lth/detailed-portfolio.aspx
    url = "http://www.morningstar.in/mutualfunds/" + id + "/x/detailed-portfolio.aspx"
    print(url)
    try:
        result = requests.get(url, proxies=proxyDict, timeout=30)
    except :
        print("Error")

    if result.status_code == 200:
        soup = BeautifulSoup(result.content, "lxml")
        name = soup.find(id="ctl00_ContentPlaceHolder1_ucQuoteHeader_lblName").get_text().strip()
        Date = soup.find(id="ctl00_ContentPlaceHolder1_lblPfSummaryDate").get_text().strip()
        month_=datetime.datetime.strptime(Date, "%d/%m/%Y").month
        if(datetime.datetime.strptime(Date, "%d/%m/%Y").month == datetime.datetime.today().month):
            newDate=Date
        table = soup.find("table", attrs={"class": "pf_detailed"})
        headings = [th.get_text() for th in table.find("tr").find_all("th")]
        tbody = table.find("tbody")

        del headings[0]
        headings = ["id", "mutual-fund"] + headings
        head_slug = [slugify(h) for h in headings]

        for row in tbody.find_all("tr")[1:]:
            temp = [td.get_text().strip() for td in row.find_all('td')]
            if temp[1] == "Total Stock":
                break
            del temp[-1]
            del temp[4]
            del temp[0]

            dataset = dict(zip(head_slug, [id, name] + temp))
            datasets.append(dataset)
             #get the change, comment as it take lots of time
            #get_change_in_mf()
    #print('\n\n\nChange in {0: <40} --> is {1}'.format(name, round((changed_weight - total_weight), 2)))


keys = list(datasets[0].keys())
# if "ratings" not in keys:
#     keys.append("rating")

with open('data.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(datasets)

combined = {}
for data in datasets:
    data["name"] = remove_words(data["name"])
    try:
        num_of_shares = int(data['number-of-shares'])
    except ValueError:
        num_of_shares = 0
    try:
        prev_num_of_shares = int(data['prev-number-of-shares'])
    except ValueError:
        prev_num_of_shares = 0

    try:
        market_value_mil = round(float(data['market-value-mil']))
    except ValueError:
        market_value_mil = 0
    try:
        prev_market_value_mil = round(float(((market_value_mil * 1000000) / num_of_shares) * prev_num_of_shares))
    except:
        prev_market_value_mil = 0

    diff = num_of_shares - prev_num_of_shares
    temp_up = []
    temp_down = []
    if diff > 0:
        temp_up.append(data["mutual-fund"])
    elif diff < 0:
        temp_down.append(data["mutual-fund"])

    if data['name'] in combined:
        combined[data['name']]["numberof-shares"] += num_of_shares
        combined[data['name']]["prev-number-of-shares"] += prev_num_of_shares
        combined[data['name']]["market-value-mil"] += market_value_mil * 1000000
        combined[data['name']]["prev-market-value-mil"] += prev_market_value_mil
        combined[data['name']]["mutual-fund"] += [data["mutual-fund"]]
        combined[data['name']]["mutual-funds-up"] += temp_up
        combined[data['name']]["mutual-funds-down"] += temp_down
    else:

        combined[data['name']] = {
            "numberof-shares": num_of_shares,
            "prev-number-of-shares": prev_num_of_shares,
            "market-value-mil": market_value_mil * 1000000,
            "prev-market-value-mil": prev_market_value_mil,
            "mutual-fund": [data["mutual-fund"]],
            "mutual-funds-up": temp_up,
            "mutual-funds-down": temp_down
        }

stocks = {}
for key, value in combined.items():
    stocks[key] = {
        "value": value['market-value-mil'] - value['prev-market-value-mil'],
        "funds-up": value["mutual-funds-up"],
        "funds-down": value["mutual-funds-down"]
    }

sorted_stocks = OrderedDict(sorted(stocks.items(), key=lambda x: x[1]['value'], reverse=True))

print("Change:")

for stock in sorted_stocks.items():
    print('{0: <40} --> {1: <15} --> {2} |||||| {3}'.format(stock[0][:40],
                                                 stock[1]['value'],
                                                 stock[1]['funds-up'],
                                                 stock[1]['funds-down']))

stocks = {}
for key, value in combined.items():
    stocks[key] = value['market-value-mil']

sorted_stocks = sorted(stocks.items(), key=operator.itemgetter(1), reverse=True)

print("\n\n\n\nValue:")
for stock in sorted_stocks:
    print('{0: <40} --> {1}'.format(stock[0][:40], stock[1]))