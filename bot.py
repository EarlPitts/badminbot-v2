from datetime import time, timedelta, timezone, date
import os

from discord.ext import tasks, commands
import discord

from poll import send_poll_req, create_poll
from utils import next_week

TOKEN = os.environ["TOKEN"]
CHAN_ID = int(os.environ["CHAN_ID"])

UTC_2 = timezone(timedelta(hours=2))
JOB_TIME = time(9,0,tzinfo=UTC_2)

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.send_poll.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(time=JOB_TIME)
    async def send_poll(self):
        if date.today().weekday() == 4: # Send the poll only on Fridays
            channel = self.get_channel(CHAN_ID)
            week_num, days = next_week(date.today())
            title = f'Tollas (hét #{week_num})'
            poll = create_poll(title, days, UTC_2)
            url = send_poll_req(lambda resp : resp.json()['url'], poll)
            await channel.send(url)

    @send_poll.before_loop
    async def before_poll(self):
        await self.wait_until_ready()  # wait until the bot logs in

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix='> ', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(TOKEN)
