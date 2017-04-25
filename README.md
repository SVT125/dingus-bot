# Dingus the Discord Bot

A Discord bot that provides useless commands and tidbits.

## Requirements

Main Requirements
* [Python 3.5+](https://www.python.org/downloads/)
* [Django](https://www.djangoproject.com/)
* [Discord.py](https://github.com/Rapptz/discord.py)

Command Dependencies
* [Google API Client Library for Python](https://developers.google.com/api-client-library/python/) (for `~google`, `~play`)
  * [Google CustomSearch Engine](https://developers.google.com/api-client-library/python/apis/customsearch/v1)
  * [Youtube Data](https://developers.google.com/api-client-library/python/apis/youtube/v3)
* [Python Reddit API Wrapper (PRAW)](https://github.com/praw-dev/praw) (for `~praw`)
* [imgurpython](https://github.com/Imgur/imgurpython) (for `~imgur`)
* [requests](https://github.com/kennethreitz/requests) (for `~gfy` and `~urban`, also a dependency for a few other APIs here)
* [validators](https://github.com/kvesteri/validators) (for simplicity of code in verifying strings against formats like web URLs)


## Commands
Note, only shorthand flags (e.g. `-r` instead of `--random`) are implemented at this moment in time.

### Information

`~data`: PM's a list of files under data\ with their full path names.

`~file`: Uploads a file to the channel. The input can be either the file's full path name or a query string to search file names with.

`~gfy`: Prints out the first gfycat gif that matches the input, which is either an actual gif ID or a query string; use flag `-r` to return a random gif from what's returned.

`~google`: Google, simply put. Use flag `-i` to search and return only images, `-r` to return a random result from what's returned. Site results will be printed with their title, URL, and short text snippet which Google matched.

`~imgur`: Search Imgur with a query string. If nothing is given, returns a random result (also available with query strings using flag `-r`). Also available are sorting flags (`-c/v/t`) and if sorting by top submissions, time window flags (`-d/w/m/y/a`).

`~reddit`: Search reddit for submissions. Use flag `-s` to specify a subset of subreddits (e.g. `-s 4chan+me_irl+...`), `-r` to return a random result from all of reddit if no input is specified, or sorting flags (`-g/h/t/n/c/i` to denote gold, hot, etc.) to sort the results.

`~urban`: Search Urban Dictionary for a term. Use flag `-r` to return a random matching definition.

### Music

`~join`: Joins the voice channel given by the input, or the voice channel that the message sender is in if no input is given.

`~leave`: Disconnects the bot from the voice channel it's in, if at all.

`~pause`: Pauses whatever the bot is playing right now.

`~play`: Plays the local or YouTube song supported by the input. YouTube URL's and search queries are supported - use flag `-r` to get a random result from what's returned instead. Use flag `-l` with a file path relative to data\ to play an audio file local to the bot's data\ folder.

`~resume`: Resumes whatever the bot had paused.

`~stop`: Stops whatever the bot is currently playing and takes the stopped audio file off its player.

`~volume`: Sets the bot's volume. 0 <= new volume <= 2, to denote volumes between 0%/muted and 200%/2x. 

### Miscellaneous

`~echo`: Echoes the input. "Slight" possibility of infinite bot conversations.

`~format`: Formats the input; moreso a shorthand versus Discord's native Markdown support, with all supported Discord text formatting also supported by this command (italics, bold, underline, etc).

`~8ball`: Your favorite magic 8 ball! Given a question (or any string argument really), returns random responses read from the bot's local text file.

`~rng`: Get a random number in between 0 and 100, although you can specify positive integer lower and upper bounds.

`~roll`: Roll a six-sided die.

`~flip`: Flip a coin - heads or tails.

