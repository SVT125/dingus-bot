from discord.ext import commands
from imgurpython import ImgurClient
from googleapiclient.discovery import build
from secrets import *
import os
import re
import random
import discord

OPUS_LIB_NAME = 'libopus-0.x86.dll'
description = "A bot that provides useless commands and tidbits. I can be found at https://github.com/SVT125/dingus-bot."
magic_ball_answers = []
bot = commands.Bot(command_prefix="~", description=description)
imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
service = build('customsearch', 'v1', developerKey=GOOGLE_KEY)


def is_flag(s):
    return re.search('-[a-zA-Z][a-zA-Z]*', s)


def startup():
    # Load the opus library for voice I/O.
    discord.opus.load_opus(OPUS_LIB_NAME)
    if discord.opus.is_loaded():
        print('Opus library successfully loaded at startup.')
    else:
        print('Failed to load opus library at startup.')

    # Reads in the magic 8 ball responses from 'resources\magicball.txt'.
    f = open('resources\magicball.txt', 'r')
    for line in f:
        magic_ball_answers.append(line.rstrip())


async def disconnect_channel(server):
    matching_voice_clients = [vc for vc in bot.voice_clients if vc.server == server]
    if matching_voice_clients:
        await matching_voice_clients[0].disconnect()


@bot.event
async def on_ready():
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('------')


@bot.command(pass_context=True)
async def file(ctx, *, args=""):
    """
    If a path is given as an argument, sends the data file found.
    Otherwise, if the argument is just a string, returns a random file with the string contained in its name.
    Use flag '' before the string to return a random file out of what's found.
    """
    matched_files = []
    # Since file paths/queries have no spaces, len(args) <= 2 and the rest of args is ignored.
    flag, path = (args.split()[0].lower(), args.split()[1].lower()) \
        if len(args.split()) > 1 and is_flag(args.split()[0]) \
        else ("", args.lower())
    is_file_path = lambda p: "." in path or "\\" in path
    match_str = path

    # If we're looking to match the argument string instead, we want to traverse all subdirs of data\.
    if path and is_file_path(path):
        sep = path.rfind('\\')
        match_str = path[sep+1:]
        path = path[0:sep]
    elif path and not is_file_path(path):
        path = ""

    for root, dirs, files in os.walk('data\\' + path):
        for file_name in files:
            if (is_file_path(path) and path == file_name.lower()) or \
                    (match_str and match_str in file_name.lower()) or \
                    not match_str:
                matched_files.append(os.path.join(root, file_name))

    if matched_files:
        chosen_file = random.choice(matched_files) if flag.lower() == '-r' else matched_files[0]
        await bot.send_file(ctx.message.channel, chosen_file)
    else:
        if is_file_path(path):
            await bot.say("Could not find a file with the given path name.")
        elif path:
            await bot.say("Could not find a file whose name contained the given string.")
        else:
            await bot.say("There are no matching files in this bot's data folder.")


# TODO - Implement rate limiting per server per day.
# TODO - Can add flags for advanced search query parameters.
@bot.command()
async def imgur(*, args=""):
    """
    Search Imgur for a picture, gif, etc.
    Supply any number of words to query by; if none are given, returns a random result.
    Note, if only the flags are given without a query, it is parsed as though the flags are the query.
    Flags available are:

    Output:
    -r  Return a random result out of what's given.

    Sort by:
    -c  Time
    -v  Viral
    -t  Top

    If sorting by top, over what time period (optional if not sorting by top):
    -d  Day
    -w  Week
    -m  Month
    -y  Year
    -a  All time
    """
    # Since file paths/queries have no spaces, len(args) <= 2 and the rest of args is ignored.
    flags, query = (args.split()[0].lower(), args.split()[1].lower()) \
        if len(args.split()) > 1 and is_flag(args.split()[0]) \
        else ("", args.lower())
    SORT_TYPES = {
        'c': 'time',
        'v': 'viral',
        't': 'top'
    }
    TIME_INTERVALS = {
        'd': 'day',
        'w': 'week',
        'm': 'month',
        'y': 'year',
        'a': 'all'
    }

    sort_flags = ''.join(SORT_TYPES)
    window_flags = ''.join(TIME_INTERVALS)
    if imgur_client.credits['ClientRemaining'] == 0:
        await bot.say("I\'m sorry, I\'ve exceeded the maximum number of imgur requests I can make today.")
        return
    if flags and len(re.findall('[' + 'r' + sort_flags + window_flags + ']', flags)) != len(flags) - 1:
        await bot.say('Invalid flags given.')
        return
    elif flags and (len(re.findall(sort_flags, flags)) > 1 or len(re.findall(window_flags, flags)) > 1):
        await bot.say("Too many sorting or time interval flags given, only 1 of each group is allowed.")
        return

    if not query:
        result = imgur_client.gallery_random(random.randint(0, 50))
        if not result:
            await bot.say('No results found.')
            return
        await bot.say(result[0].link)
    else:
        sort = SORT_TYPES.get(re.search('[' + sort_flags + ']', flags).group(0), 'top') \
            if re.search('[' + sort_flags + ']', flags) else 'top'
        window = TIME_INTERVALS.get(re.search('[' + window_flags + ']', flags).group(0), 'all') \
            if re.search('[' + window_flags + ']', flags) else 'all'
        result = imgur_client.gallery_search(query, sort=sort, window=window)
        if not result:
            await bot.say('No results found.')
            return
        if re.search('r', flags):
            await bot.say(random.choice(result).link)
        else:
            await bot.say(result[0].link)


@bot.command(pass_context=True)
async def data(ctx):
    """
    PM's the list of files in the data folder.
    """
    msg = "Hi! These are the contents of Dingus' data directory.\n" \
          "====================================\n"
    for root, dirs, files in os.walk('data\\'):
        for file_name in files:
            msg += os.path.join(root, file_name) + '\n'
    await bot.send_message(ctx.message.author, msg)


# TODO - Potentially implement leaving the channel after a period of time -> keeps open vc list in check, faster ops.
@bot.command(pass_context=True)
async def join(ctx, channel=""):
    """
    Joins the channel specified.
    If no channel is given, joins the channel of the user who ran the command.
    """
    server = ctx.message.server
    if not discord.opus.is_loaded():
        discord.opus.load_opus(OPUS_LIB_NAME)

    # If the bot is currently connected to a channel on this server, disconnect first.
    await disconnect_channel(server)

    if channel:
        found_channel = [c for c in server.channels if c.name == channel]
        try:
            await bot.join_voice_channel(found_channel[0])
        except Exception as err:
            if not discord.opus.is_loaded():
                await bot.say('Opus library failed to load; you probably need to restart me.')
            else:
                await bot.say('Unknown error occurred.\n{}'.format(err))
    else:
        if not ctx.message.author.voice.voice_channel:
            await bot.say('User is not in a voice channel!')
            return
        try:
            await bot.join_voice_channel(ctx.message.author.voice.voice_channel)
        except Exception as err:
            if err == discord.InvalidArgument:
                await bot.say('Invalid voice channel given.')
            elif not discord.opus.is_loaded():
                await bot.say('Opus library failed to load; you probably need to restart me.')
            else:
                await bot.say('Unknown error occurred.\n{}'.format(err))


@bot.command(pass_context=True)
async def leave(ctx):
    """
    Disconnects the bot from its current voice channel.
    """
    server = ctx.message.server
    await disconnect_channel(server)


# TODO - Allow users to add their own responses.
# TODO - If command starts with !, it can't be erased; circumvent people deleting ! insertions as well.
# TODO - Don't use server's file, but a local file of name "<server ID>-fortune.txt", to stop constant r/w.
@bot.command()
async def magic8(question=""):
    """
    Your favorite magic 8 ball!
    Given a question (or any string argument really), returns a random response from a file.
    """
    if not question:
        await bot.say('You didn\'t ask the magic 8 ball a question!')
    else:
        await bot.say(random.choice(magic_ball_answers))


@bot.command()
async def echo(*, msg):
    """
    Echoes the arguments at the end of the command.
    Useful(?) for improvising a little bot to bot conversation.
    """
    await bot.say(msg)


# TODO - More intrinsic exception reporting e.g. what actually sets off query limit reached?
@bot.command()
async def google(*, args=""):
    """
    Do a google text or image search.
    Use flag -i to do an image search; otherwise, it'll be a text search.
    Use flag -r to return a random result of what's found.
    """
    flags, query = (args.split()[0].lower(), args.split()[1].lower()) \
        if len(args.split()) > 1 and is_flag(args.split()[0]) \
        else ("", args.lower())
    is_img_search = 'image' if re.search('i', flags) else None
    start = 1 if re.search('r', flags) else random.randint(1, 10)
    try:
        results = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=10,filter='1',
                                    start=start, searchType=is_img_search, safe='off').execute()['items']
    except Exception as e:
        await bot.say('Oops! Something went wrong with the Google query - I might\'ve run out of my queries for today.')
        print(e)
        return
    if not results:
        await bot.say('No results were found for this query.')
    else:
        selected = random.choice(results) if re.search('r', flags) else results[0]
        await bot.say('**{} ({})**\n{}'.format(selected['title'], selected['link'], selected['snippet']))


def get_bot():
    startup()
    return bot
