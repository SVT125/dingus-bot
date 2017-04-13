from discord.ext import commands
from imgurpython import ImgurClient
from secrets import *
import os
import re
import random
import discord

OPUS_LIB_NAME = 'libopus-0.x86.dll'
description = "A bot that provides useless commands and tidbits. I can be found at https://github.com/SVT125/dingus-bot."
bot = commands.Bot(command_prefix=">", description=description)
imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)

discord.opus.load_opus(OPUS_LIB_NAME)
if discord.opus.is_loaded():
    print('Opus library successfully loaded at startup.')
else:
    print('Failed to load opus library at startup.')


def is_flag(s):
    return re.search('-[a-zA-Z][a-zA-Z]*', s)


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


# TODO - Consider sorting by time, viral, top (c, v, t) and by top e.g. day, week, month, year, all (d, w, m, y, a)
@bot.command(pass_context=True)
async def imgur(ctx, *, args=""):
    """
    Search Imgur for a picture, gif, etc.
    Supply any number of words to query by. Add -r to return a random result of what's found.
    Otherwise, if no argument is given, returns a random result anyway.
    """
    # Since file paths/queries have no spaces, len(args) <= 2 and the rest of args is ignored.
    flag, query = (args.split()[0].lower(), args.split()[1].lower()) \
        if len(args.split()) > 1 and is_flag(args.split()[0]) \
        else ("", args.lower())
    if flag and flag != '-r':
        await bot.say('Invalid arguments given.')
    elif flag == '-r' or (not flag and not query):
        # TODO - Random.
        pass
    else:
        # TODO - Return first result of query.
        imgur_client.gallery_search(query)


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


def get_bot():
    return bot
