import os, sys
import asyncio

# Add the root directory of codes to the sys.path
par_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(par_dir)

from telegram.ext import ApplicationBuilder
from private.constants import CRYAMBLE_BOT_API_KEY, NOTI_CHANNEL_ID, MONEYFUCKER_CHANNEL_ID


class Bot:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.application = ApplicationBuilder().token(CRYAMBLE_BOT_API_KEY).build()

    async def run(self):
        # print("Bot running...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        # await self.send_signals(f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}\nBot started...")  # Optional: notify when bot starts
        # await self.application.updater.idle()

    async def stop(self):
        # await self.send_signals(f"Shutting down bot...")  # Optional: notify before shutting down
        await self.application.stop()

    async def send_signals(self, message):
        await self.application.bot.send_message(chat_id=self.channel_id, text=message)
        

def bot_test(channel_id):
    bot = Bot(channel_id)
    async def test():
        await bot.run()
        await bot.send_signals("Test message from bot...")
    asyncio.run(test())
    pass


if __name__ == "__main__":
    channel = sys.argv[1]
    channel_id = MONEYFUCKER_CHANNEL_ID if channel.casefold() == "moneyfucker" else NOTI_CHANNEL_ID
    bot_test(channel_id)
    