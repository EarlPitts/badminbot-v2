from datetime import time, date
from random import choice
from time import sleep
from time import time as unixtime
import os

from discord.ext import tasks, commands
import discord

from chatbot import chat
from poll import *
import utils

TOKEN = os.environ["TOKEN"]
CHAN_ID = int(os.environ["CHAN_ID"])
ADMIN = int(os.environ["ADMIN"])
STRAWPOLL_API_KEY = os.environ["STRAWPOLL_API_KEY"]

JOB_TIME = time(9,0)
CONFIG_FILENAME = 'config.json'
JOKES_FILENAME = 'jokes.txt'

class MyBot(commands.Bot):
    """Sets up bot object (mainly for defining recurrent tasks)"""

    def __init__(self, *args, **kwargs):
        self.config = utils.load_config(CONFIG_FILENAME)
        self.jokes = utils.load_jokes(JOKES_FILENAME)
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.send_poll.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(time=JOB_TIME)
    async def send_poll(self, force=False):
        if (utils.is_thursday() or force is True) and self.config['days'] != []: # Send the poll only on Thursdays
            channel = self.get_channel(CHAN_ID)
            active_day = lambda day: day.weekday() in self.config['days']
            week_num, days = utils.next_week(date.today())
            active_days = filter(active_day, days)
            title = f'Tollas (hét #{week_num})'
            start, end = self.config['time']
            hours = range(start, end)
            poll = create_poll(title, active_days, hours)
            url = create_poll_req(lambda resp : resp.json()['url'], poll, STRAWPOLL_API_KEY)
            await channel.send(url)

    @send_poll.before_loop
    async def before_poll(self):
        await self.wait_until_ready()  # wait until the bot logs in

    async def close_poll(self, id):
        channel = self.get_channel(CHAN_ID)
        poll = get_poll_req(lambda resp: resp.json(), id, STRAWPOLL_API_KEY)
        poll['poll_config']['deadline_at'] = int(unixtime())
        status = update_poll_req(lambda resp: resp.status_code, id, poll, STRAWPOLL_API_KEY)
        if status == 200:
            await channel.send('Sure thing, I closed it!')
        else:
            await channel.send("Sorry, I just can't do it. :(")

intents = discord.Intents.default()
intents.message_content = True

bot = MyBot(command_prefix='!', intents=intents)

@bot.listen()
async def on_message(message):
    """Sends message to local model if the bot is mentioned"""
    if bot.user in message.mentions:
        async with message.channel.typing():
            resp = chat(message.content)
            await message.reply(resp)

@bot.listen()
async def on_message(message):
    """Pin message containing the poll url"""
    if message.author.id == bot.user.id and 'strawpoll.com' in message.content:
        await message.pin()

@bot.command()
async def joke(ctx):
    """Tells a very funny joke"""
    await ctx.send(choice(bot.jokes))

@bot.command()
async def poll(ctx):
    """Send the poll now"""
    if ctx.message.author.id == ADMIN:
        await bot.send_poll(force=True)

@bot.command()
async def close_poll(ctx, id: str):
    """Close the given poll"""
    if ctx.message.author.id == ADMIN:
        await bot.close_poll(id)

@bot.command()
async def get_schedule(ctx):
    """Shows which days will be in the next poll"""
    if ctx.message.author.id == ADMIN:
        await ctx.send(f'Schedule for poll is: {list(map(utils.show_day, bot.config["days"]))}')

@bot.command()
async def schedule(ctx, *days: int):
    """Modify next week's poll by specifying the days using numbers 0 to 6"""
    if ctx.message.author.id == ADMIN:
        bot.config['days'] = days # TODO Handle wrong input
        utils.modify_config(bot.config, CONFIG_FILENAME)
        print(f'Schedule modified: {days}')
        await ctx.send(f'Schedule was modified to: {list(map(utils.show_day, days))}')

@bot.command()
async def shutup(ctx):
    """Temporarily turns off the polls"""
    if ctx.message.author.id == ADMIN:
        bot.config['days'] = []
        utils.modify_config(bot.config, CONFIG_FILENAME)
        print(f'Polls turned off')
        await ctx.send(f'All right, turning off polls.')

@bot.command()
async def schedule_hours(ctx, *hours: int):
    """Modify next week's poll by specifying time slots"""
    if ctx.message.author.id == ADMIN:
        bot.config['time'] = hours # TODO Handle wrong input
        utils.modify_config(bot.config, CONFIG_FILENAME)
        print(f'Timeslots modified: {hours[0]} - {hours[1]}')
        await ctx.send(f'Timeslots were modified to: {hours[0]} - {hours[1]}')

@bot.command()
async def get_timeslots(ctx):
    """Show timeslots for next poll"""
    if ctx.message.author.id == ADMIN:
        start, end = bot.config['time']
        await ctx.send(f'Timeslots for poll: {start} - {end}')

@bot.command()
async def call(ctx, target):
    """Call's the reception of target"""
    await ctx.send(f'Calling {target}...')
    sleep(5)
    if (target == "Tüskecsarnok" or target == "Tüske") and date.today().weekday() < 5:
        await ctx.send(f'They said they are full and then condescendingly reprimanded me for calling them in the first place during the working days of the week.')
    else:
        await ctx.send(f'Unfortunately, no response...')

bot.run(TOKEN)
