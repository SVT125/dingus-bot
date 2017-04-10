import discord
from discord.ext import commands
import asyncio

description="A bot that provides useless commands and tidbits. I can be found at https://github.com/SVT125/dingus-bot."
bot = commands.Bot(command_prefix=">", description=description)
help_message = "Hello! Below are the commands available to you: " \
    "TODO"


@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('------')

@bot.command
@asyncio.coroutine
def help():
    yield from bot.say(help_message)


def get_bot():
    return bot
