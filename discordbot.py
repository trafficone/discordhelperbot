#!/usr/bin/env python
import random
from github import Github
from datetime import datetime, date, timedelta
from pprint import pprint
import discord
from discord.ext import commands
from boardgamegeek import BGGClient, BGGRestrictSearchResultsTo


#this is seriously naughty
g = Github()


def get_key(keyfile='.keyfile'):
    with open(keyfile, 'r') as f:
        key = f.read().strip()
    return key


def get_latest_push(repo='trafficone/discordhelperbot'):
    return (g.get_repo().pushed_at - datetime.now()).seconds


def search_boardgame(boardgame, game_type=None):
    """
    Uses the boardgamemeek XML API to search for games
    Currently supports boardgames and TT RPGS
    """
    if game_type is None:
        search_type = None
        game_type = 'boardgame'
    elif game_type == 'RPG':
        game_type = 'rpgitem'
        search_type = [BGGRestrictSearchResultsTo.RPG]
    bgg = BGGClient()
    res = bgg.search(boardgame, search_type=search_type)
    # this is terrible
    if len(res) == 0:
        return "I couldn't find any game similar to the title %s" % boardgame
    print([x.data() for x in res[0:10]])
    games = [x for x in res if boardgame.lower() == x.name.lower()]
    resp = ""
    if len(games) == 0:
        resp += ("Couldn't find game {} exactly, but I found {} which " +
                 "looks close\n").format(boardgame, len(res))
        games = [x for x in res if boardgame.lower() in x.name.lower()]
        if len(games) == 0:
            resp += "Well, not exactly close, "
            resp += "but here's the oldest one on the list\n"
            games = res
    g = sorted(games, key=lambda x: x.year)[0]
    url_format = "https://www.boardgamegeek.com/{game_tp}/{id}/{name}".format(
                    game_tp=game_type,
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
    """Searches BoardGameGeek for a boardgame"""
    try:
        bg_url = search_boardgame(' '.join(game))
    except Exception:
        await ctx.send("Error occurred searching boardgame")
        return
    await ctx.send(bg_url)


@bot.command()
async def rpg(ctx, *game: str):
    """Searches BoardGameGeek for an RPG"""
    try:
        bg_url = search_boardgame(' '.join(game), game_type='RPG')
    except Exception as e:
        print(e)
        await ctx.send("Error occurred searching RPG")
        return
    await ctx.send(bg_url)


@bot.command()
async def add(ctx, left: float, right: float):
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

    if rolls > 100 or rolls < 1 or limit < 1:
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
    print(choices)
    choices = [x for x in choices if len(x) > 0]
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


@bot.command()
async def santa(ctx):
    """Calculates days until "christmas" """
    giftday = date(2020, 12, 27)
    shipday = date(2020, 12, 12)
    wishday = date(2020, 11, 27)
    today = date.today()
    msg = "Ho ho ho! "
    if (wishday-today).days > 0:
        msg += f"you have {(wishday-today).days} days to complete your wishlist"
    elif (shipday-today).days > 0:
        msg += f"you have {(shipday-today).days} days to ship your gifts"
    elif (giftday-today).days > 0:
        msg += f"we will open our gifts in {(giftday-today).days} days. Dec 27 at 4 pm ET / 3 pm CT / 2 pm AZ / 1 pm PT"
    else:
        "the secret santa event is over"
    await ctx.send(msg)


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
