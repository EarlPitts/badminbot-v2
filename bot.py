from datetime import time, timedelta, timezone, date
import os

from discord.ext import tasks, commands
import discord

from poll import send_poll_req, create_poll
import utils

TOKEN = os.environ["TOKEN"]
CHAN_ID = int(os.environ["CHAN_ID"])
ADMIN = int(os.environ["ADMIN"])

UTC_2 = timezone(timedelta(hours=2))
JOB_TIME = time(9,0,tzinfo=UTC_2)
ACTIVE_DAYS_FILENAME = 'days.json'

class MyBot(commands.Bot):
    """
    Sets up bot object (mainly for defining recurrent tasks)
    """

    def __init__(self, *args, **kwargs):
        self.days = utils.load_schedule(ACTIVE_DAYS_FILENAME)
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.send_poll.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(time=JOB_TIME)
    async def send_poll(self, force=False):
        if (date.today().weekday() == 4 or force is True) and self.days != []: # Send the poll only on Fridays
            channel = self.get_channel(CHAN_ID)
            active_day = lambda day: day.weekday() in self.days
            week_num, days = utils.next_week(date.today())
            active_days = filter(active_day, days)
            title = f'Tollas (hét #{week_num})'
            poll = create_poll(title, active_days, UTC_2)
            url = send_poll_req(lambda resp : resp.json()['url'], poll)
            await channel.send(url)

    @send_poll.before_loop
    async def before_poll(self):
        await self.wait_until_ready()  # wait until the bot logs in

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix='!', intents=intents)

@bot.command()
async def poll(ctx):
    if ctx.message.author.id == ADMIN:
        await bot.send_poll(force=True)

@bot.command()
async def schedule(ctx, *days: int):
    if ctx.message.author.id == ADMIN:
        bot.days = days # TODO Handle wrong input
        utils.modify_schedule(days, ACTIVE_DAYS_FILENAME)
        print(f'Schedule modified: {days}')
        await ctx.send(f'Schedule was modified to: {list(map(utils.show_day, days))}')

bot.run(TOKEN)
