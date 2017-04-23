from discord.ext import commands
from imgurpython import ImgurClient
from googleapiclient.discovery import build
from cogs.music import OPUS_LIB_NAME
from cogs.utils.utils import *
from secrets import *
import discord
import praw

description = "A bot that provides useless commands and tidbits. " \
              "I can be found at https://github.com/SVT125/dingus-bot.\n" \
              "Note, all flags in commands are shorthand and must be written under 1 argument e.g. -ibu, ib, etc."

bot = commands.Bot(command_prefix="~", description=description)

extensions = [
    'cogs.information',
    'cogs.music',
    'cogs.miscellaneous',
]


def startup():
    # Load the opus library for voice I/O.
    discord.opus.load_opus(OPUS_LIB_NAME)
    if discord.opus.is_loaded():
        print('Opus library successfully loaded at startup.')
    else:
        print('Failed to load opus library at startup.')

    # Reads in the magic 8 ball responses from 'resources\magicball.txt'.
    f = open('resources\magicball.txt', 'r')
    bot.magic_ball_answers = []
    for line in f:
        bot.magic_ball_answers.append(line.rstrip())
    print('Loaded magic 8 ball answers from file.')

    # Loads the API clients.
    bot.imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
    bot.yt_search_service = build('youtube', 'v3', developerKey=GOOGLE_KEY)
    bot.search_service = build('customsearch', 'v1', developerKey=GOOGLE_KEY)
    bot.reddit_instance = praw.Reddit(client_id=REDDIT_APP_ID,
                                  client_secret=REDDIT_APP_SECRET,
                                  user_agent=REDDIT_APP_USER_AGENT)

    # Gets the gfycat access token to begin with.
    if refresh_gfy_token(refresh=False):
        print('Successfully authenticated gfycat on startup.')
    else:
        print('Unable to authenticate gfycat ID and secret. Skipping...')

    # Load all extensions/cogs since we should have loaded all prerequisites by this point.
    for ext in extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print(e)
            print('Failed to load extension {}: {}'.format(ext, e))


@bot.event
async def on_ready():
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('------')


def get_bot():
    startup()
    return bot
