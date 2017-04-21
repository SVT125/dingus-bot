from discord.ext import commands
from imgurpython import ImgurClient
from googleapiclient.discovery import build
from cogs.utils.utils import *
from secrets import *
import discord
import random
import praw
import os

OPUS_LIB_NAME = 'libopus-0.x86.dll'
description = "A bot that provides useless commands and tidbits. " \
              "I can be found at https://github.com/SVT125/dingus-bot.\n" \
              "Note, all flags in commands are shorthand and must be written under 1 argument e.g. -ibu, ib, etc."
magic_ball_answers = []
music_players = {} # <K = server ID, V = music player>

bot = commands.Bot(command_prefix="~", description=description)

extensions = [
    'cogs.information',
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
    for line in f:
        magic_ball_answers.append(line.rstrip())
    print('Loaded magic 8 ball answers from file.')

    # Loads the API clients.
    bot.imgur_client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
    bot.service = build('customsearch', 'v1', developerKey=GOOGLE_KEY)
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


async def disconnect_channel(server):
    matching_voice_clients = [vc for vc in bot.voice_clients if vc.server == server]
    if matching_voice_clients:
        await matching_voice_clients[0].disconnect()


@bot.event
async def on_ready():
    print('Logged in as {} (ID: {})'.format(bot.user.name, bot.user.id))
    print('------')


@bot.command()
async def file(*, args=""):
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

    # A bare security check to ensure we aren't sending files above data\.
    if '..' in path:
        await bot.say('Can\'t send a file above data\\\, you dingus!')
        return

    for root, dirs, files in os.walk('data\\' + path):
        for file_name in files:
            if (is_file_path(path) and path == file_name.lower()) or \
                    (match_str and match_str in file_name.lower()) or \
                    not match_str:
                matched_files.append(os.path.join(root, file_name))

    if matched_files:
        chosen_file = random.choice(matched_files) if flag.lower() == '-r' else matched_files[0]
        await bot.upload(chosen_file)
    else:
        if is_file_path(path):
            await bot.say("Could not find a file with the given path name.")
        elif path:
            await bot.say("Could not find a file whose name contained the given string.")
        else:
            await bot.say("There are no matching files in this bot's data folder.")


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


# TODO - Support multiple paths at once + queue of songs.
# TODO - Support local data playback.
# TODO - Support playing songs found by query.
# TODO - Show downloading + now playing statements.
'''
In particular, src_type is either yt or local.
If src_type = yt, then uses the path as a URL or a matching substring.
Else, if src_type = local then searches using the path as either a path or a matching substring.
File extension supported for playing locally are .mp3, .mp4.
'''
@bot.command(pass_context=True)
async def play(ctx, *, path):
    """
    Plays the song given by the URL.
    """
    global music_players
    if not bot.voice_client_in(ctx.message.server):
        await bot.say('I\'m not in a voice channel to play music, you dingus!')
        return

    vc = bot.voice_client_in(ctx.message.server)
    player = await vc.create_ytdl_player(path)
    music_players[ctx.message.server.id] = player
    player.start()

    song_duration = '{}:{}'.format(player.duration // 60, str(player.duration % 60).zfill(2)) if player.duration else \
        '-1'
    song_title = '{}'.format(player.title) if player.title else player.download_url
    if song_duration != '-1':
        song_title += (' ({})'.format(song_duration))
    await bot.say('Downloading and playing **{}**...'.format(song_title))


@bot.command(pass_context=True)
async def pause(ctx):
    """
    Pauses the bot's music.
    """
    player = music_players[ctx.message.server.id]
    player.pause()
    song_title = player.title if player.title else player.url
    await bot.say('Pausing **{}**'.format(song_title))


@bot.command(pass_context=True)
async def resume(ctx):
    """
    Resumes the bot's music.
    """
    player = music_players[ctx.message.server.id]
    player.resume()
    song_title = player.title if player.title else player.url
    await bot.say('Resuming **{}**'.format(song_title))


@bot.command(pass_context=True)
async def stop(ctx):
    """
    Stops the bot's music and discards the song played.
    """
    player = music_players[ctx.message.server.id]
    player.stop()
    song_title = player.title if player.title else player.url
    await bot.say('Stopping **{}**'.format(song_title))


@bot.command(pass_context=True)
async def volume(ctx, volume):
    """
    Sets the bot's music volume.
    The volume can be a value between 0 (mute, 0%) to 2 (2x volume, 200%).
    """
    if not volume:
        await bot.say('You didn\'t specify a volume, you dingus.')
        return

    try:
        if float(volume) < 0 or float(volume) > 2:
            raise ValueError
    except ValueError:
        await bot.say('Volume values can only be between 0 and 2.')
        return

    player = music_players[ctx.message.server.id]
    player.volume = float(volume)
    await bot.say('Music volume set to **{}**.'.format(volume))


def get_bot():
    startup()
    return bot
