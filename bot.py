import discord
from discord.ext import commands
import asyncio

description="A bot that provides useless commands and tidbits. I can be found at https://github.com/SVT125/dingus-bot."
bot = commands.Bot(command_prefix=">", description=description)


@bot.event
async def on_ready():
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('------')

@bot.command()
async def test():
    await bot.say("6")


def get_bot():
    return bot
