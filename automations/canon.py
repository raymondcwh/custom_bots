import os, sys
import asyncio
import requests
from bs4 import BeautifulSoup
import datetime as dt

# Add the root directory of codes to the sys.path
par_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(par_dir)

from private.constants import NOTI_CHANNEL_ID
from bot.tg_bot import Bot

CANON_HK_URL = 'https://store.hk.canon/chinese/'
G7X = CANON_HK_URL + 'powershot-g7-x-mark-iii.html'


def check_g7x_in_stock():
    try:
        response = requests.get(G7X, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        product_info = soup.find('div', class_='product-info-main')
        product_stock = product_info.find('div', class_='product-info-stock-sku')
        unavailable_display = product_stock.find('div', class_='stock unavailable').get('style', '')
        if len(unavailable_display):
            return 1    # Indicate in stock
        else:
            return 0    # Indicate out of stock
    except requests.RequestException as e:
        return -1   # Indicate an error occurred
    

async def notify_channel(product):
    if product.casefold() == "g7x":
        in_stock = check_g7x_in_stock()
        product_url = G7X
    else:
        return
    # print('running check_g7x_in_stock:', in_stock)

    bot = Bot(NOTI_CHANNEL_ID)
    await bot.run()
    if in_stock > 0:
        message = f"{product} is in stock now! Click {product_url}"
    elif in_stock < 0:
        message = f"Error occurred when checking {product} stock."
    else:
        hk_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
        if hk_now.minute == 0:
            message = f"{product} monitor still running at {hk_now.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            message = ""
    if message:
        await bot.send_signals(message)
    await bot.stop()
    pass


if __name__ == "__main__":
    product = sys.argv[1].upper()
    asyncio.run(notify_channel(product))