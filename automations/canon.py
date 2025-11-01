import os, sys
import asyncio
import requests
from bs4 import BeautifulSoup
import datetime as dt
import re

# Add the root directory of codes to the sys.path
par_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(par_dir)

from private.constants import NOTI_CHANNEL_ID
from bot.tg_bot import Bot

CANON_HK_URL = 'https://store.hk.canon/chinese/'
G7X = CANON_HK_URL + 'powershot-g7-x-mark-iii.html'
# G7X = CANON_HK_URL + 'powershotv1.html'


def check_g7x_in_stock():
    try:
        response = requests.get(G7X, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        product_info = soup.find('div', class_='product-info-main')
        g7x_list = product_info.find('table', class_='table data grouped').find('tbody').find_all('tr')
        g7x_general = product_info.find('div', class_='product-info-stock-sku').find('div', class_='stock unavailable')
        availability = []
        for item in g7x_list:
            item_name = item.find(class_='product-item-name').text.strip()
            item_colour = re.search(r'\((.*?)\)', item_name).group(1)
            available_div = item.find('div', class_='stock available')
            unavailable_div = item.find('div', class_='stock unavailable')
            if (available_div is not None) and ((unavailable_div is None) or len(unavailable_div.get('style', ''))):
                availability.append(item_colour)
        if (g7x_general is not None) and (g7x_general.get('style', '')):
            availability.append('')
            # print(available_div, unavailable_div)
        return availability   # Indicate in stock colours
    except requests.RequestException as e:
        return f"Error checking G7X stock: {e}"
    

async def notify_channel(product):
    if product.casefold() == "g7x":
        in_stock = check_g7x_in_stock()
        product_url = G7X
    else:
        return
    # print('running check_g7x_in_stock:', in_stock) 
    # return

    bot = Bot(NOTI_CHANNEL_ID)
    # await bot.run()
    if isinstance(in_stock, list):
        if len(in_stock):
            message = f"{product} {' & '.join(in_stock).strip()} in stock now! Click {product_url}"
        else:
            hk_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
            if hk_now.minute == 0:
                message = f"{product} monitor still running at {hk_now.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                message = ""   
                # message = f"{product} monitor still running at {hk_now.strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        message = in_stock  # Error message
        
    if message:
        await bot.send_signals(message)
    # await bot.stop()
    pass


if __name__ == "__main__":
    product = sys.argv[1].upper()
    asyncio.run(notify_channel(product))