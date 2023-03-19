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
