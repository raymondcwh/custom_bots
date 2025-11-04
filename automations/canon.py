import os, sys, time, argparse
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
        g7x_general = product_info.find('div', class_='product-info-stock-sku').find('div', class_='stock available')
        availability = []
        stock_info = {}
        if g7x_general:
            for item in g7x_list:
                item_name = item.find(class_='product-item-name').text.strip()
                item_colour = re.search(r'\((.*?)\)', item_name).group(1)
                qty = item.find('td', class_='col qty').find('div').text.strip()
                stock_info[item_colour] = qty
                unavailable_div = item.find('div', class_='stock unavailable')
                if qty.isnumeric() or (qty == '') or (unavailable_div is None) or (unavailable_div.text.strip() == ''):
                    availability.append(item_colour)
            # available_div = item.find('div', class_='stock available')
            # unavailable_div = item.find('div', class_='stock unavailable')
            # if (available_div is not None) and ((unavailable_div is None) or len(unavailable_div.get('style', ''))):
            #     availability.append(item_colour)
            # print(available_div, unavailable_div)
        else:
            general_stock = product_info.find('div', class_='product-info-stock-sku').find('div', class_='stock unavailable')
            stock_info['G7X'] = general_stock.text.strip() if general_stock else ''
        return (availability, stock_info)  # Indicate in stock colours
    except requests.RequestException as e:
        return f"Error checking G7X stock: {e}"
    

async def notify_channel(product, run_times=1, sleep_secs=10):
    check_message = True
    while run_times > 0:
        if product.casefold() == "g7x":
            check_result = check_g7x_in_stock()
            if isinstance(check_result, tuple):
                in_stock, stock_info = check_result
            else:
                in_stock = check_result
            product_url = G7X
        else:
            return
        # print('running check_g7x_in_stock:', in_stock)
        # return

        bot = Bot(NOTI_CHANNEL_ID)
        # await bot.run()
        if isinstance(in_stock, list):
            print(stock_info)
            if len(in_stock):
                message = f"{product} {' & '.join(in_stock).strip()} in stock now! Click {product_url}"
            else:
                hk_now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
                if ((hk_now.minute % 20) == 0) and check_message:
                    message = f"{product} monitor still running at {hk_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    for colour, qty in stock_info.items():
                        message += f"{colour}: {qty}\n"
                    check_message = False
                else:
                    message = ""   
                    # message = f"{product} monitor still running at {hk_now.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            message = in_stock  # Error message
            
        if message:
            await bot.send_signals(message)
        # await bot.stop()
        run_times -= 1
        time.sleep(sleep_secs)
    pass


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", "--product", dest="product",
                            default='g7x',
                            help="Canon product to monitor")
    argparser.add_argument("-t", "--run_times", dest="run_times", type=int,
                            default=1,
                            help="number of times to run the check")
    argparser.add_argument("-s", "--sleep_secs", dest="sleep_secs", type=int,
                            default=10,
                            help="seconds to sleep between checks")
    opts = argparser.parse_args()
    asyncio.run(notify_channel(opts.product.upper(), opts.run_times, opts.sleep_secs))