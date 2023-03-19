import requests
from bs4 import BeautifulSoup

url = 'https://www.moneycontrol.com/mutual-funds/idbi-india-top-100-equity-fund-direct-plan/portfolio-holdings/MIB092'

response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

rows = soup.select('#equityCompleteHoldingTable > tbody > tr')

data_array = []

for row in rows:
    data = row.get_text().strip().split('\n')
    data_array.append([data[1], data[6]]) # extract only the 2nd and 8th columns and append to data_array

print(data_array)