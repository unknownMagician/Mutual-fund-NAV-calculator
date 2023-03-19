import aiohttp
import asyncio

async def fetch_stock_price(session, company_name):
    async with session.get(f'https://www.moneycontrol.com/financials/{company_name}/ratiosVI/{company_name}-4#4') as response:
        response_text = await response.text()
        start_pos = response_text.find("LTP: </strong>")
        end_pos = response_text.find("<span class='gr_11'")
        if start_pos == -1 or end_pos == -1:
            return None
        stock_price = response_text[start_pos:end_pos].split()[-1].replace(",", "")
        return stock_price

async def get_stock_price(company_name):
    async with aiohttp.ClientSession() as session:
        stock_price = await fetch_stock_price(session, company_name)
        return stock_price

async def main():
    company_names = ["Reliance Industries", "Tata Consultancy Services", "HDFC Bank"]
    tasks = []
    for company_name in company_names:
        task = asyncio.create_task(get_stock_price(company_name))
        tasks.append(task)
    stock_prices = await asyncio.gather(*tasks)
    print(stock_prices)

if __name__ == '__main__':
    asyncio.run(main())
