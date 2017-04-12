from discord.ext import commands
import os
import random
import discord

OPUS_LIB_NAME = 'libopus-0.x86.dll'
description = "A bot that provides useless commands and tidbits. I can be found at https://github.com/SVT125/dingus-bot."
bot = commands.Bot(command_prefix=">", description=description)

discord.opus.load_opus(OPUS_LIB_NAME)
if discord.opus.is_loaded():
    print('Opus library successfully loaded at startup.')
else:
    print('Failed to load opus library at startup.')


async def disconnect_channel(server):
    matching_voice_clients = [vc for vc in bot.voice_clients if vc.server == server]
    if matching_voice_clients:
        await matching_voice_clients[0].disconnect()


@bot.event
async def on_ready():
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('------')


@bot.command(pass_context=True)
async def file(ctx, path=""):
    """
    If a path is given as an argument, sends the data file found.
    Otherwise, if the argument is just a string, returns a random file with the string contained in its name.
    Else, sends a random file.
    """
    matched_files = []
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
        chosen_file = random.choice(matched_files)
        await bot.send_file(ctx.message.channel, chosen_file)
    else:
        if is_file_path(path):
            await bot.say("Could not find a file with the given path name.")
        elif path:
            await bot.say("Could not find a file whose name contained the given string.")
        else:
            await bot.say("There are no files in this bot's data folder to send.")


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