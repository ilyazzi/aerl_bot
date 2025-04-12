import os
import asyncio
import datetime
import logging
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot

TOKEN = "8144728704:AAFGr9cCa7sc8TO3TBtT9G757RLfujXKmv8"
CHAT_ID = 484768320

URL_TEMPLATE = "https://www.aeroflot.ru/sb/catalog/offers?origin=SU&Moscow&destination=KGD&adults=2&children=3&infants=0&cabin=economy&tripType=oneway&departureDate={date}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

async def fetch_price(session, date_str):
    url = URL_TEMPLATE.format(date=date_str)
    async with session.get(url, headers=HEADERS) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        prices = soup.find_all('span', class_='product_price__value')  # class may change
        if prices:
            try:
                price_text = prices[0].get_text().replace(' ', '').replace('₽', '').strip()
                price = int(price_text)
                return date_str, price, url
            except:
                return date_str, None, url
        return date_str, None, url

async def main():
    bot = Bot(token=TOKEN)
    today = datetime.date.today()
    start_date = datetime.date(2025, 7, 1)
    end_date = datetime.date(2025, 7, 30)
    dates = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, d) for d in dates]
        results = await asyncio.gather(*tasks)

    message_lines = []
    min_price = None
    min_date = None
    for date, price, link in results:
        if price:
            message_lines.append(f"{date}: {price}₽")
            if not min_price or price < min_price:
                min_price = price
                min_date = date

    if message_lines:
        summary = f"
Минимум: {min_price}₽ на {min_date}" if min_price else ""
        message = "
".join(message_lines) + summary
    else:
        message = "Билеты не найдены или сайт недоступен."

    await bot.send_message(chat_id=CHAT_ID, text=message)

if __name__ == "__main__":
    asyncio.run(main())