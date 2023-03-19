import requests
from bs4 import BeautifulSoup

def get_stock_price(company_name):
    # Send request to BSE search page
    response = requests.get(f"https://www.bseindia.com/corporates/List_Scrips.aspx?expandable=1&letter={company_name[0]}")

    # Parse HTML response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find table rows containing company names and symbols
    rows = soup.find_all('tr')

    # Search for company name in BSE table rows
    for row in rows[1:]:
        cols = row.find_all('td')
        if cols[0].text.strip() == company_name.upper():
            symbol = cols[1].text.strip()
            break
    else:
        # If company not found in BSE, search in NSE
        response = requests.get(f"https://www.nseindia.com/market-data/stocks-futures/options-chain?symbol={company_name.upper()}")
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', text=lambda t: t.startswith('var underlyingSymbol ='))
        try:
            symbol = script.text.split("'")[1]
        except (AttributeError, IndexError):
            print('Invalid company name')
            return None

    # Send request to Alpha Vantage API
    api_key = 'YWE3W4NN8ZC3T4EC'  # Replace with your API key
    response = requests.get(f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}")

    # Parse JSON response
    data = response.json()

    # Extract current stock price from response
    try:
        price = float(data['Global Quote']['05. price'])
        return price
    except (KeyError, ValueError):
        print('Invalid stock symbol')
        return None

# Example usage
company_name = input('Enter company name: ')

price = get_stock_price(company_name)
if price is not None:
    print(f'The current stock price for {company_name} is Rs. {price:.2f}')

