from discord.ext import commands
from cogs.utils.utils import is_flag
import random


class Miscellaneous:
    # For commands that don't fit anywhere else or are arguably useless or arbitrary.

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def echo(self, *, msg=""):
        """
        Echoes the arguments at the end of the command.
        Useful(?) for improvising a little bot to bot conversation.
        """
        if not msg:
            await self.bot.say('Give me something to echo, you dingus!')
            return
        await self.bot.say(msg)

    @commands.command()
    async def format(self, *, args=""):
        """
        Formats the input.
        Note, Discord natively supports text formatting (goo.gl/7cFz0f), but this is just a lazy shorthand.
        Flags available are:

        -i  Italics
        -b  Bold
        -s  Strikeout
        -u  Underline
        -o  One/single line code block
        -m  Multi-line code block
        -l  Specific language formatting (applicable only with code blocks)

        Italics, bold, and underline (-i, -b, -u) can be used in combination e.g. -ib, -bu, etc.
        Use -l to allow highlighting of a given language when also using code blocks (-l has no effect without -o/-m).
        If -l is enabled, the first argument after the flags must be the language name.
        Code block/language formatting overrides all other flags, while strikeout overrides italics/bold/underline.
        """
        flags = args.split()[0][1:] if is_flag(args.split()[0]) else ""
        text = args[len(flags) + 2:] if flags and len(args) > len(flags) + 2 else args
        if len(args) == len(flags) + 1:
            await self.bot.say('You didn\'t put any text, dingus!')
            return

        if 'm' in flags:
            if 'l' in flags and len(args.split()) <= 1:
                await self.bot.say('No language was specified for syntax highlighting (and you included -l)!')
                return
            elif 'l' in flags:
                language = text.split()[0]
                text = text[len(language) + 1:]
                output = '```{}\n{}```'.format(language, text)
                await self.bot.say(output)
                return
            output = '```\n{}```'.format(text)
        elif 'o' in flags:
            output = '`{}`'.format(text)
        elif 's' in flags:
            output = '~~{}~~'.format(text)
        else:
            output = text
            if 'i' in flags:
                output = '*' + output + '*'
            if 'b' in flags:
                output = '**' + output + '**'
            if 'u' in flags:
                output = '__' + output + '__'
        await self.bot.say(output)

    # TODO - Allow users to add their own responses.
    # TODO - If command starts with !, it can't be erased; circumvent people deleting ! insertions as well.
    # TODO - Don't use server's file, but a local file of name "<server ID>-fortune.txt", to stop constant r/w.
    @commands.command(name='8ball')
    async def magic8(self, question=""):
        """
        Your favorite magic 8 ball!
        Given a question (or any string argument really), returns a random response from a file.
        """
        if not question:
            await self.bot.say('You didn\'t ask the magic 8 ball a question!')
        else:
            await self.bot.say(random.choice(self.bot.magic_ball_answers))

    @commands.command()
    async def rng(self, *, args=""):
        """
        Get a random number.
        The default range is [0, 100], but you can specify lower and upper bounds in the input.
        e.g. ~rng 2 50 gets a random number in [2, 50].
        """
        lower = 0
        upper = 100
        if args:
            if len(args.split()) != 2 or not args.replace(' ', '').isdigit():
                await self.bot.say('You need to give me a numeric positive lower and upper bound if you\'re '
                                   'giving input, you dingus!')
                return
            args = args.split()
            lower, upper = int(args[0]), int(args[1])
            if lower > upper:
                await self.bot.say('The lower bound can\'t be greater than the upper bound, you dingus!')
                return

        result = random.randint(lower, upper)
        await self.bot.say('Your random number is **{}.**'.format(result))

    @commands.command()
    async def roll(self):
        """
        Roll the dice.
        Returns a value between 1 to 6, like your traditional die.
        """
        result = random.randint(1, 6)
        await self.bot.say('You rolled a **{}!**'.format(result))

    @commands.command()
    async def flip(self):
        """
        Flip a coin.
        """
        result = 'HEADS' if random.randint(0, 1) else 'TAILS'
        await self.bot.say('You flipped a coin and got __**{}**__!'.format(result))


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
