from discord.ext import commands
from cogs.utils.utils import *
import discord
import random

OPUS_LIB_NAME = 'libopus-0.x86.dll'


class Music:
    # For music related commands e.g. song playback.

    def __init__(self, bot):
        self.bot = bot
        self.music_players = {}  # <K = server ID, V = music player>

    async def disconnect_channel(self, server):
        matching_voice_clients = [vc for vc in self.bot.voice_clients if vc.server == server]
        if matching_voice_clients:
            await matching_voice_clients[0].disconnect()

    async def display_no_song_error(self):
        await self.bot.say('I currently don\'t have any songs in queue.')

    @commands.command(pass_context=True)
    async def join(self, ctx, *, channel=""):
        """
        Joins the channel specified.
        If no channel is given, joins the channel of the user who ran the command.
        """
        server = ctx.message.server
        if not discord.opus.is_loaded():
            discord.opus.load_opus(OPUS_LIB_NAME)

        # If the bot is currently connected to a channel on this server, disconnect first.
        await self.disconnect_channel(server)

        if channel:
            found_channel = [c for c in server.channels if c.name == channel]
            try:
                await self.bot.join_voice_channel(found_channel[0])
            except Exception as err:
                if not discord.opus.is_loaded():
                    await self.bot.say('Opus library failed to load; you probably need to restart me.')
                else:
                    await self.bot.say('Unknown error occurred.\n{}'.format(err))
        else:
            if not ctx.message.author.voice.voice_channel:
                await self.bot.say('User is not in a voice channel!')
                return
            try:
                await self.bot.join_voice_channel(ctx.message.author.voice.voice_channel)
            except Exception as err:
                if err == discord.InvalidArgument:
                    await self.bot.say('Invalid voice channel given.')
                elif not discord.opus.is_loaded():
                    await self.bot.say('Opus library failed to load; you probably need to restart me.')
                else:
                    await self.bot.say('Unknown error occurred.\n{}'.format(err))

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        """
        Disconnects the bot from its current voice channel.
        """
        server = ctx.message.server
        await self.disconnect_channel(server)

    # TODO - Support multiple paths at once + queue of songs.
    # TODO - Show downloading + now playing statements asynchronously.
    @commands.command(pass_context=True)
    async def play(self, ctx, *, args=""):
        """
        Plays the song given by the URL/found by the query.
        If the arguments are not recognized as a web URL, they are assumed to be a search query.
        
        Use flag -r for search queries to return a random result of what's found.
        Use flag -l to search for a file locally in the bot's data directory.
        """
        server_id = ctx.message.server.id

        if not args:
            await self.bot.say('You didn\'t give me anything to play, you dingus!')
            return

        if not self.bot.voice_client_in(ctx.message.server):
            await self.bot.say('I\'m not in a voice channel to play music, you dingus!')
            return

        if server_id in self.music_players and self.music_players[server_id].is_playing():
            await self.bot.say('Sorry, I can\'t queue any songs right now. I\'m a dingus.')
            return

        flags, query = (args.split()[0].lower(), ' '.join(args.split()[1:])) \
            if len(args.split()) > 1 and is_flag(args.split()[0]) \
            else ("", args)
        vc = self.bot.voice_client_in(ctx.message.server)

        if 'l' in flags:
            """
            TODO - It's possible to play a non-audio file, since we can't view ffmpeg's outputs via discord.py.
            it might be feasible to whitelist only a list of file extensions + 
            prevent RTL overrides, view entire file and its extension(s), etc.
            """
            matched_file_path = find_files(query, return_all=False)
            if not matched_file_path:
                await self.bot.say('No files found.')
                return

            player = vc.create_ffmpeg_player(matched_file_path)
            self.music_players[server_id] = player
            player.start()

            await self.bot.say('Now playing local file: **{}**...'.format(matched_file_path))
        else:
            if not is_web_url(args):
                results = self.bot.yt_search_service.search().list(part='snippet', maxResults=25, q=query).execute()
                if 'items' not in results:
                    await self.bot.say('No Results found.')
                    return
                result = random.choice(results['items']) if 'r' in flags else results['items'][0]
                video_url = 'https://www.youtube.com/watch?v={}'.format(result['id']['videoId'])
            else:
                video_url = query

            player = await vc.create_ytdl_player(video_url)
            self.music_players[server_id] = player
            player.start()

            song_duration = '{}:{}'.format(player.duration // 60, str(player.duration % 60).zfill(2)) if player.duration \
                else '-1'
            song_title = '{}'.format(player.title) if player.title else player.download_url
            if song_duration != '-1':
                song_title += (' ({})'.format(song_duration))
            await self.bot.say('Downloading and playing **{}**...'.format(song_title))

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        """
        Pauses the bot's music.
        """
        player = self.music_players.get(ctx.message.server.id, None)
        if not player or player.is_done():
            await self.display_no_song_error()
            return

        player.pause()
        song_title = player.title if player.title else player.url
        await self.bot.say('Pausing **{}.**'.format(song_title))

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        """
        Resumes the bot's music.
        """
        player = self.music_players.get(ctx.message.server.id, None)
        if not player or player.is_done():
            await self.display_no_song_error()
            return

        player.resume()
        song_title = player.title if player.title else player.url
        await self.bot.say('Resuming **{}.**'.format(song_title))

    @commands.command(pass_context=True)
    async def stop(self, ctx):
        """
        Stops the bot's music and discards the song played.
        """
        player = self.music_players.get(ctx.message.server.id, None)
        if not player or player.is_done():
            await self.display_no_song_error()
            return

        player.stop()
        song_title = player.title if player.title else player.url
        await self.bot.say('Stopping **{}.**'.format(song_title))

    # TODO - Allow ~volume to show current volume; implement server_id -> curr_volume mapping to set volume w/o player on.
    @commands.command(pass_context=True)
    async def volume(self, ctx, volume):
        """
        Sets the bot's music volume.
        The volume can be a value between 0 (mute, 0%) to 2 (2x volume, 200%).
        """
        if not volume:
            await self.bot.say('You didn\'t specify a volume, you dingus.')
            return

        try:
            if float(volume) < 0 or float(volume) > 2:
                raise ValueError
        except ValueError:
            await self.bot.say('Volume values can only be between 0 and 2.')
            return

        player = self.music_players[ctx.message.server.id]
        player.volume = float(volume)
        await self.bot.say('Music volume set to **{}**.'.format(volume))


def setup(bot):
    bot.add_cog(Music(bot))