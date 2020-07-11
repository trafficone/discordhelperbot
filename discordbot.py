import random
import discord
from discord.ext import commands
from boardgamegeek import BGGClient


def get_key(keyfile='.keyfile'):
    with open(keyfile, 'r') as f:
        key = f.read().strip()
    return key


def search_boardgame(boardgame):
    bgg = BGGClient()
    res = bgg.search(boardgame)
    """
    res[i].data() = return dict of boardgame data
    keys are "yearpublished", "id", "name", "type"
    res[i].name = name of game
    res[i].id = id number of game (BGG ID)
    NOTE: BGG URL is https://www.boardgamegeek.com/boardgame/{id}/{name}
    but name is optional
    """
    # this is terrible
    if len(res) == 0:
        return "I couldn't find any game similar to the title %s" % boardgame
    print([x.data() for x in res[0:10]])
    games = [x for x in res if boardgame.lower() == x.name.lower()]
    resp = ""
    if len(games) == 0:
        resp += ("Couldn't find boardgame {} exactly, but I found {} which " +
                 "looks close\n").format(boardgame, len(res))
        games = [x for x in res if boardgame.lower() in x.name.lower()]
        if len(games) == 0:
            resp += "Well, not exactly close, "
            resp += "but here's the oldest one on the list\n"
            games = res
    g = sorted(games, key=lambda x: x.year)[0]
    url_format = "https://www.boardgamegeek.com/boardgame/{id}/{name}".format(
                    id=g.id,
                    name=g.name.lower().replace(' ', '-'))
    return resp+url_format


description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='?', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def bg(ctx, *game: str):
    try:
        bg_url = search_boardgame(' '.join(game))
    except Exception:
        await ctx.send("Error occurred searching boardgame")
        return
    await ctx.send(bg_url)


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    if rolls > 100 or rolls < 0 or limit < 0:
        await ctx.send('Invalid roll.')
        return

    try:
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    except Exception:
        await ctx.send('Could not process roll. Sorry.')
        return

    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    # for i in range(times):
    await ctx.send(content)
    await ctx.send("Imagine I sent that %d times" % times)


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send('{0.name} joined in {0.joined_at}'.format(member))


@bot.command()
async def tableflip(ctx):
    """Flip a table"""
    flips = """
    (╯°□°）╯︵ ┻━┻
    (┛◉Д◉)┛彡┻━┻
    (ノಠ益ಠ)ノ彡┻━┻
    (╯ರ ~ ರ）╯︵ ┻━┻
    (┛ಸ_ಸ)┛彡┻━┻
    (ノಥ,_｣ಥ)ノ彡┻━┻
    (┛✧Д✧))┛彡┻━┻""".split('\n')
    await ctx.send(random.choice(flips))


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        msg = random.choice(['cool', 'not cool'])
        await ctx.send('{0.subcommand_passed} is/are {1}'.format(ctx, msg))


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

bot.run(get_key())
