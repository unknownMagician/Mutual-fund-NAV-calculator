# import asyncio
# import aiohttp
# import async_timeout
# from bs4 import BeautifulSoup

# # Use a connection pool to reuse HTTP connections
# CONN_POOL = aiohttp.TCPConnector(limit=10)

# async def fetch_stock_price(session, company_name):
#     # Use async_timeout to set a timeout for the HTTP request
#     async with async_timeout.timeout(10):
#         # Use aiodns to perform DNS resolution asynchronously
#         async with session.get(f'https://www.moneycontrol.com/financials/{company_name}/ratiosVI/{company_name}-4#4') as response:
#             # Use a faster HTML parser library such as lxml or html5lib
#             html = await response.text()
#             soup = BeautifulSoup(html, 'html5lib')
#             stock_price = soup.select_one('.FL.PR5 span').text.strip()
#             return stock_price

# async def get_stock_price(company_name):
#     async with aiohttp.ClientSession(connector=CONN_POOL) as session:
#         stock_price = await fetch_stock_price(session, company_name)
#         return stock_price

# async def main():
#     # Query stock prices for multiple companies concurrently
#     company_names = ['reliance-industries', 'tata-consultancy-services', 'hdfc-bank']
#     tasks = [get_stock_price(company_name) for company_name in company_names]
#     stock_prices = await asyncio.gather(*tasks)
#     print(stock_prices)

# if __name__ == '__main__':
#     asyncio.run(main())
import yfinance as yf

# Set the company name
company_name = "Apple Inc."

# Get the stock ticker symbol for the company
company = yf.Ticker(company_name)
ticker_symbol = company.info['symbol']

# Get the current stock price for the company
stock_data = yf.download(ticker_symbol, period='1d', interval='1m')
current_price = stock_data['Close'][-1]

# Print the stock price
print("The current stock price of " + company_name + " is: $" + str(current_price))



