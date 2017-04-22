from discord.ext import commands
from cogs.utils.utils import *
from prawcore.exceptions import ResponseException
import re
import os
import random


class Information:
    # For commands that dispense information and data from sites,

    def __init__(self, bot):
        self.bot = bot

    # TODO - Can add flags for advanced search query parameters.
    @commands.command()
    async def imgur(self, *, args=""):
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
        flags, query = (args.split()[0].lower()[1:], args.split()[1].lower()) \
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
        if self.bot.imgur_client.credits['ClientRemaining'] == 0:
            await self.bot.say("I\'m sorry, I\'ve exceeded the maximum number of imgur requests I can make today.")
            return
        if flags and len(re.findall('[r{}]'.format(sort_flags + window_flags), flags)) != len(flags):
            await self.bot.say('Invalid flags given.')
            return
        elif flags and (len(re.findall(sort_flags, flags)) > 1 or len(re.findall(window_flags, flags)) > 1):
            await self.bot.say("Too many sorting or time interval flags given, only 1 of each group is allowed.")
            return

        if not query:
            result = self.bot.imgur_client.gallery_random(random.randint(0, 50))
            if not result:
                await self.bot.say('No results found.')
                return
            await self.bot.say(result[0].link)
        else:
            sort = SORT_TYPES.get(re.search('[{}]'.format(sort_flags), flags).group(0), 'top') \
                if re.search('[{}]'.format(sort_flags), flags) else 'top'
            window = TIME_INTERVALS.get(re.search('[{}]'.format(window_flags), flags).group(0), 'all') \
                if re.search('[{}]'.format(window_flags), flags) else 'all'
            result = self.bot.imgur_client.gallery_search(query, sort=sort, window=window)
            if not result:
                await self.bot.say('No results found.')
                return
            if re.search('r', flags):
                await self.bot.say(random.choice(result).link)
            else:
                await self.bot.say(result[0].link)

    @commands.command()
    async def data(self):
        """
        PM's the list of files in the data folder.
        """
        msg = "Hi! These are the contents of Dingus' data directory.\n"
        msg += ("=" * len(msg)) + '\n'
        for root, dirs, files in os.walk('data\\'):
            for file_name in files:
                msg += os.path.join(root, file_name) + '\n'
        await self.bot.whisper(msg)


    @commands.command()
    async def file(self, *, args=""):
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
            match_str = path[sep + 1:]
            path = path[0:sep]
        elif path and not is_file_path(path):
            path = ""

        # A bare security check to ensure we aren't sending files above data\.
        if '..' in path:
            await self.bot.say('Can\'t send a file above data\\\, you dingus!')
            return

        for root, dirs, files in os.walk('data\\' + path):
            for file_name in files:
                if (is_file_path(path) and path == file_name.lower()) or \
                        (match_str and match_str in file_name.lower()) or \
                        not match_str:
                    matched_files.append(os.path.join(root, file_name))

        if matched_files:
            chosen_file = random.choice(matched_files) if flag.lower() == '-r' else matched_files[0]
            await self.bot.upload(chosen_file)
        else:
            if is_file_path(path):
                await self.bot.say("Could not find a file with the given path name.")
            elif path:
                await self.bot.say("Could not find a file whose name contained the given string.")
            else:
                await self.bot.say("There are no matching files in this bot's data folder.")

    # TODO - More intrinsic exception reporting e.g. what actually sets off query limit reached?
    # TODO - Print diff stmt for no results.
    @commands.command()
    async def google(self, *, args=""):
        """
        Do a google text or image search.
        Use flag -i to do an image search; otherwise, it'll be a text search.
        Use flag -r to return a random result of what's found.
        """
        flags, query = (args.split()[0].lower(), args.split()[1:]) \
            if len(args.split()) > 1 and is_flag(args.split()[0]) \
            else ("", args.lower())
        is_img_search = 'image' if re.search('i', flags) else None
        start = random.randint(1, 10) if re.search('r', flags) else 1
        try:
            results = self.bot.service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=10, filter='1',
                                         start=start, searchType=is_img_search, safe='off').execute()
            if 'items' not in results:
                await self.bot.say('No results found.')
                return
            results = results['items']
        except Exception as e:
            await self.bot.say(
                'Oops! Something went wrong with the Google query - I might\'ve run out of my queries for today.')
            return

        if not results:
            await self.bot.say('No results were found for this query.')
        else:
            selected = random.choice(results) if re.search('r', flags) else results[0]
            if is_img_search:
                await self.bot.say('{}'.format(selected['link']))
            else:
                await self.bot.say('**{} ({})**\n{}'.format(selected['title'], selected['link'], selected['snippet']))

    @commands.command()
    async def gfy(self, *, args=""):
        """
        Searches for a gfycat gif.
        Use flag -r to return a random gif of what's found.
        Use flag -n to get a gif by its name e.g. DelayedArtisticGuppy.
        """
        flags, query = (args.split()[0].lower(), args.split()[1].lower()) \
            if len(args.split()) > 1 and is_flag(args.split()[0]) \
            else ("", args.lower())
        if 'n' in flags:
            response = request_gfy('https://api.gfycat.com/v1/gfycats/{}'.format(query))
            if not response:
                await self.bot.say('Woops! This command isn\'t working right now, please try again later!')
                return
            result = response.json()
            if 'errorMessage' in result:
                await self.bot.say('The given gfycat name is invalid!')
            else:
                await self.bot.say(result['gfyItem']['gifUrl'])
        else:
            payload = {
                'search_text': query,
                'count': 25
            }
            response = request_gfy('https://api.gfycat.com/v1/gfycats/search', params=payload)
            result, status_code = response.json(), response.status_code
            if not response or 'errorMessage' in result:
                await self.bot.say('Woops! This command isn\'t working right now, please try again later!')
                return
            else:
                if 'r' in flags:
                    result_gif = random.choice(result['gfycats'])
                else:
                    result_gif = result['gfycats'][0]
                await self.bot.say(result_gif['gifUrl'])

    # TODO - Allow for long-form command specification for -s flag e.g. -subreddit=4chan+me_irl+...
    # TODO - Support searching for redditors and "hopefully" pulling random comments - annoying since no random indexing.
    # TODO - Can add more flags e.g. sort top by time window, etc.
    @commands.command()
    async def reddit(self, *, args=""):
        """
        Retrieves Reddit posts.
        Use flag -r to return a random result only if you haven't specified a search term (just a random bag grab).
        Use flag -s to search under the given subreddits; if this flag is used, the subreddit(s) must be the next argument.
        You can specify multiple subreddits to search by appending them together with +'s in between.
        e.g. 4chan+me_irl+greentext...

        The following flags are available for sorting subreddit posts:
        -g  Gilded
        -h  Hot
        -t  Top
        -n  New
        -c  Controversial
        -i  Rising

        If no sorting flag is specified, the query defaults to returning the first submission under the "hot" list.
        -r takes precedence over any of the sorting flags (-g/h/t/n/c/i).
        """
        flags, query = (args.split()[0].lower()[1:], ' '.join(args.split()[1:])) \
            if len(args.split()) > 1 and is_flag(args.split()[0]) \
            else ("", args.lower())

        if len(re.findall('[rsghtnci]', flags)) != len(flags):
            await self.bot.say('Invalid flags given.')
            return

        if len(re.findall('[ghtnci]', flags)) > 1:
            await self.bot.say('You put too many sorting flags in, you dingus!')
            return

        subreddits, query = (query.split()[0], ' '.join(query.split()[1:])) if 's' in flags else ('all', query)
        selected_subreddits = self.bot.reddit_instance.subreddit(subreddits)
        SORT_FUNCTIONS = {
            'g': selected_subreddits.gilded,
            'h': selected_subreddits.hot,
            't': selected_subreddits.top,
            'n': selected_subreddits.new,
            'c': selected_subreddits.controversial,
            'i': selected_subreddits.rising
        }
        sort_types = ''.join(SORT_FUNCTIONS)

        # Either we're searching with a query or we're returning a submission given the parameters.
        subreddit_results = selected_subreddits.search(query, limit=25) if query else \
            SORT_FUNCTIONS.get(re.search('[{}]'.format(sort_types), flags).group(0),
                               selected_subreddits.hot)(limit=25)

        try:
            if not query and 'r' in flags:
                await self.bot.say(selected_subreddits.random().shortlink)
            else:
                await self.bot.say(next(subreddit_results).shortlink)
        except ResponseException:
            await self.bot.say('Invalid subreddit query provided!')


def setup(bot):
    bot.add_cog(Information(bot))