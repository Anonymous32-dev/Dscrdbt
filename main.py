# main.py - Byte X Selfbot (FULL Nighty Command Set + Extra)
# Recovered from Nighty by Byte X / gang.baby
#
# pip install curl_cffi==0.9.0 aiohttp requests
#
# Runs on the discord fork bundled in lib/ - the exact bytecode
# Nighty.exe shipped. No discord packages needed from pip.
#
# 226 commands. Zero auth. Zero paywall. Zero nighty.one APIs.

import asyncio
import base64
import hashlib
import json
import logging
import os
import random
import re
import string
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.version_info[:2] != (3, 8):
    print("=" * 60)
    print(" [!] Python 3.8 is REQUIRED to run this selfbot.")
    print(f" Current version: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(" The bundled discord core in lib/ requires Python 3.8 bytecode.")
    print(" Run 'setup.bat' or install Python 3.8 (winget install Python.Python.3.8)")
    print("=" * 60)
    input(" Press Enter to exit...")
    sys.exit(1)

# his own discord fork ships in lib/ - same bytecode the exe ran on.
# put lib/ first on the path so it wins over any pip discord package.
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, 'lib'))

try:
    import curl_cffi
    # his bundled build adds one export stock pip lacks
    if not hasattr(curl_cffi, 'WebSocketError'):
        class WebSocketError(curl_cffi.CurlError):
            pass
        curl_cffi.WebSocketError = WebSocketError
except ImportError:
    print('curl_cffi is not installed.')
    print()
    print('  run: pip install curl_cffi==0.9.0')
    print()
    input('press enter to exit...')
    exit(1)

try:
    import aiohttp  # noqa: F401 - his http layer needs it
except ImportError:
    print('aiohttp is not installed.')
    print()
    print('  run: pip install aiohttp')
    print()
    input('press enter to exit...')
    exit(1)

try:
    import google.protobuf  # noqa: F401
except ImportError:
    print('protobuf is not installed.')
    print()
    print('  run: pip install protobuf')
    print()
    input('press enter to exit...')
    exit(1)

try:
    import discord
    if getattr(discord, '__version__', '') != '2.2.0a':
        raise ImportError('wrong discord loaded')
except ImportError:
    print('could not load the bundled discord fork from lib/.')
    print()
    print('  keep the lib/ folder next to main.py, it ships with the repo.')
    print()
    input('press enter to exit...')
    exit(1)

from discord.ext import commands, tasks

try:
    import requests
except ImportError:
    requests = None

# ============================================================
#  CONFIG
# ============================================================
TOKEN = os.environ.get("DISCORD_TOKEN", "PASTE_YOUR_DISCORD_TOKEN_HERE")
PREFIX = "."
NITRO_WEBHOOK = ""
AFK_MESSAGE = "I'm AFK right now, I'll get back to you."
AUTO_REACT_EMOJI = ""

# ============================================================
#  DATA
# ============================================================
DATA_DIR = Path(os.environ.get('APPDATA', '.')) / 'ByteX-Selfbot'
DATA_DIR.mkdir(exist_ok=True)

def _load(name, default=None):
    p = DATA_DIR / name
    try:
        return json.loads(p.read_text())
    except Exception:
        return default if default is not None else {}

def _save(name, data):
    (DATA_DIR / name).write_text(json.dumps(data, indent=2))

CONFIG = _load('config.json')
if (not TOKEN or TOKEN == "PASTE_YOUR_DISCORD_TOKEN_HERE") and CONFIG.get('token'):
    TOKEN = CONFIG['token']
RPC_PRESETS = _load('rpc_presets.json')
ALIASES = _load('aliases.json')
REMINDERS = _load('reminders.json', [])
SNIPED_MESSAGES = {}
EDIT_SNIPED = {}

# ============================================================
#  STATE
# ============================================================
AFK = False
AFK_SINCE = None
SNIPE_COUNT = 0
GIVEAWAY_COUNT = 0
START_TIME = time.time()
KEYWORD_RESPONSES = {}
AUTO_REACT_ENABLED = bool(AUTO_REACT_EMOJI)
CYCLE_STATUSES = []
CYCLE_INDEX = 0
CYCLE_TASK = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Byte X] %(levelname)s: %(message)s'
)
log = logging.getLogger('bytex')

bot = commands.Bot(command_prefix=PREFIX, help_command=None)
bot._skip_check = lambda x, y: False


@bot.event
async def on_ready():
    log.info(f'Logged in as {bot.user} ({bot.user.id})')
    log.info(f'Prefix: {PREFIX} | {len(bot.commands)} commands loaded')
    log.info('Byte X Selfbot | gang.baby | Credits or get mogged')


# ============================================================
#  HELPER: styled embed
# ============================================================
def bx_embed(title='', desc='', color=0x000000):
    e = discord.Embed(title=title, description=desc, color=color)
    e.set_footer(text='Byte X | gang.baby')
    return e


def _format_embed(embed):
    parts = []
    if getattr(embed, 'author', None) and getattr(embed.author, 'name', None):
        parts.append(f"**{embed.author.name}**")
    if getattr(embed, 'title', None) and embed.title:
        parts.append(f"**{embed.title}**")
    if getattr(embed, 'description', None) and embed.description:
        parts.append(embed.description)
    if getattr(embed, 'fields', None):
        for field in embed.fields:
            if field.name and field.value:
                parts.append(f"**{field.name}**: {field.value}")
    if getattr(embed, 'footer', None) and getattr(embed.footer, 'text', None):
        parts.append(f"*{embed.footer.text}*")
    return "\n".join(parts)

_orig_send = discord.abc.Messageable.send

async def _patched_send(self, content=None, **kwargs):
    embed = kwargs.pop('embed', None)
    embeds = kwargs.pop('embeds', None)
    embed_texts = []
    if embed is not None:
        t = _format_embed(embed)
        if t:
            embed_texts.append(t)
    if embeds:
        for em in embeds:
            t = _format_embed(em)
            if t:
                embed_texts.append(t)
    if embed_texts:
        combined = "\n\n".join(embed_texts)
        if content:
            content = f"{content}\n\n{combined}"
        else:
            content = combined
    return await _orig_send(self, content=content, **kwargs)

discord.abc.Messageable.send = _patched_send


# ============================================================
#  HELP
# ============================================================
CATEGORIES = {
    'general': [
        'ping', 'tokeninfo', 'uptime', 'avatar', 'banner', 'whois',
        'serverinfo', 'guildicon', 'credits', 'alias', 'remind',
        'time', 'calculate', 'random', 'coinflip', 'roll', '8ball',
        'choose', 'rate', 'password', 'ghostmode', 'stealthmode',
        'notificationsound', 'unpin', 'forward', 'webhook', 'read',
        'pin', 'quote', 'typing'
    ],
    'troll': [
        'hypesquad', 'embed', 'dm', 'massdm', 'purge', 'spam',
        'ghostping', 'quickdelete', 'fakemention', 'react', 'unreact',
        'poll', 'say', 'echo', 'empty', 'spacer', 'multiline',
        'fakemessage', 'wipe', 'scare', 'slowspam', 'autodelete',
        'typestart', 'typestop'
    ],
    'text': [
        'clap', 'sarcasm', 'vaporwave', 'bold', 'italic', 'underline',
        'strike', 'spoiler', 'code', 'reverse', 'upper', 'lower',
        'count', 'morse', 'translate', 'supreme', 'starwars',
        'bandname', 'joke', 'fact', 'advice', 'affirmation',
        'showerthought', 'unpopular', 'zalgo', 'tinytext',
        'bubbletext', 'squaretext', 'fancytext', 'strikethrough',
        'header', 'bullet', 'numbered', 'checkbox', 'typewriter',
        'flash', 'wavetext', 'rainbowtext'
    ],
    'spotify': [
        'spotify', 'play', 'skip', 'queue'
    ],
    'rpc': [
        'rpc', 'stream', 'rpcoff', 'rpcpreset', 'cycle', 'dnd',
        'idle', 'online', 'invisible', 'setstatus', 'setabout',
        'setpronouns', 'listening', 'watching', 'competing',
        'playing', 'setavatar', 'setbanner'
    ],
    'auto': [
        'afk', 'autoreact', 'keyword', 'nitro', 'givesnipe',
        'autorespond', 'triggerlist', 'triggerdel', 'schedule',
        'cancelschedule'
    ],
    'server': [
        'channelinfo', 'rolelist', 'botlist', 'inrole', 'mods',
        'admins', 'owner', 'joindate', 'serverlist', 'boost',
        'pins', 'invite', 'invites', 'roleinfo', 'boosters',
        'serveremojis', 'stealemoji', 'nick', 'setname',
        'slowmode', 'massnick', 'massrole', 'auditlog', 'modlog',
        'emojiinfo', 'emojidel', 'emojirename', 'stickers'
    ],
    'user': [
        'unfriend', 'block', 'unblock', 'connections', 'email',
        'nitroinfo', 'guildcount', 'friendcount', 'blockcount',
        'pending', 'relationship', 'messagecount', 'wordcount',
        'serverstats', 'leaderboard', 'oldestfriend', 'newestfriend',
        'mutualservers', 'mutualfriends', 'discriminator',
        'avatarhistory', 'friendall'
    ],
    'backup': [
        'backupfriends', 'backupservers', 'backupemojis',
        'firstmessage', 'copyembed'
    ],
    'fun': [
        'rps', 'minesweeper', 'tictactoe', 'urban', 'crypto',
        'weather', 'meme', 'reddit', 'cat', 'dog', 'fox', 'shibe',
        'bird', 'wiki', 'dictionary', 'chart', 'nft'
    ],
    'calc': [
        'calculate', 'time', 'countdown', 'stopwatch', 'base64',
        'hex', 'binary', 'url', 'rot13', 'hash', 'uuid',
        'snowflake', 'timestamp', 'gif', 'imgur', 'qr',
        'addreactions', 'clearreactions', 'note', 'notes',
        'tag', 'mytags', 'tagdel'
    ],
    'snipe': [
        'snipe', 'editsnipe', 'afklist'
    ],
    'voice': [
        'voicestate', 'deafen', 'selfmute', 'screenshare', 'camera'
    ]
}

CATEGORY_DESCS = {
    'general': 'Utility basics',
    'troll': 'Trolling commands',
    'text': 'Text formatting & generators',
    'spotify': 'Spotify controls',
    'rpc': 'Rich Presence & status',
    'auto': 'Automation & snipers',
    'server': 'Server management & info',
    'user': 'User profile & relationships',
    'backup': 'Backup & recovery',
    'fun': 'Fun & games',
    'calc': 'Calculators & dev tools',
    'snipe': 'Message sniping',
    'voice': 'Voice controls',
}

COMMAND_TO_CAT = {}
for _cat, _cmds in CATEGORIES.items():
    for _cmd in _cmds:
        COMMAND_TO_CAT[_cmd] = _cat

@bot.command(name='help')
async def help_cmd(ctx, category=''):
    cat = category.strip().lower()
    if not cat:
        e = bx_embed('Byte X Selfbot',
                     f'*Nighty but free and without the phone home*\n'
                     f'Use `{PREFIX}help <category>` or `{PREFIX}help all`\n\n')
        for k, desc in CATEGORY_DESCS.items():
            cmd_count = len(CATEGORIES.get(k, []))
            e.add_field(name=f"{k.title()} ({cmd_count})",
                        value=f"`{PREFIX}help {k}` - {desc}", inline=True)
        e.add_field(name='Total',
                    value=f'**{len(bot.commands)}** commands',
                    inline=True)
        await ctx.send(embed=e)
    elif cat == 'all':
        cmds = sorted([c.name for c in bot.commands])
        lines = [f'`{PREFIX}{name}`' for name in cmds]
        for i in range(0, len(lines), 30):
            await ctx.send(' '.join(lines[i:i+30]))
    elif cat in CATEGORIES:
        cmds = CATEGORIES[cat]
        lines = [f'`{PREFIX}{name}`' for name in sorted(cmds)]
        e = bx_embed(f"Commands: {cat.title()} ({len(cmds)})",
                     CATEGORY_DESCS.get(cat, ''))
        e.add_field(name='Commands', value=', '.join(lines), inline=False)
        await ctx.send(embed=e)
    elif cat in COMMAND_TO_CAT or bot.get_command(cat):
        c_name = cat
        cmd_obj = bot.get_command(c_name)
        c_cat = COMMAND_TO_CAT.get(c_name, 'misc')
        doc = (getattr(cmd_obj, 'short_doc', '') or '').strip()
        e = bx_embed(f"Command: {PREFIX}{c_name}")
        e.add_field(name='Category', value=f"`{c_cat}`", inline=True)
        e.add_field(name='Usage', value=f"`{PREFIX}{c_name}`", inline=True)
        if doc:
            e.add_field(name='Description', value=doc, inline=False)
        await ctx.send(embed=e)
    else:
        matching_cats = [k for k in CATEGORIES if cat in k]
        matching_cmds = [c.name for c in bot.commands if cat in c.name]
        if matching_cats:
            return await help_cmd(ctx, matching_cats[0])
        elif matching_cmds:
            lines = [f'`{PREFIX}{name}`' for name in sorted(matching_cmds)]
            e = bx_embed(f"Commands matching '{cat}' ({len(matching_cmds)})")
            e.add_field(name='Matches', value=', '.join(lines), inline=False)
            return await ctx.send(embed=e)
        valid_cats = ', '.join(f'`{k}`' for k in CATEGORIES)
        await ctx.send(f':x: Unknown category `{category}`.\nValid categories: {valid_cats}\nOr use `{PREFIX}help all`.')


# ============================================================
#  GENERAL / UTILITY
# ============================================================
@bot.command(name='ping')
async def ping_cmd(ctx):
    start = time.perf_counter()
    msg = await ctx.send('pinging...')
    ms = (time.perf_counter() - start) * 1000
    await msg.edit(content=f'`{ms:.0f}ms` | gw `{bot.latency*1000:.0f}ms`'
                  f' | sniped `{SNIPE_COUNT}`')


@bot.command(name='tokeninfo')
async def tokeninfo_cmd(ctx):
    u = bot.user
    e = bx_embed('Account Info')
    e.add_field(name='Username', value=str(u))
    e.add_field(name='ID', value=u.id)
    e.add_field(name='Created',
                value=u.created_at.strftime('%Y-%m-%d'))
    e.add_field(name='Nitro',
                value=str(u.premium_type) if u.premium_type else 'None')
    e.add_field(name='AFK', value='Yes' if AFK else 'No')
    if u.avatar:
        e.set_thumbnail(url=u.avatar.url)
    await ctx.send(embed=e)


@bot.command(name='uptime')
async def uptime_cmd(ctx):
    s = int(time.time() - START_TIME)
    h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    await ctx.send(f'**{h}h {m}m {sec}s** | nitro `{SNIPE_COUNT}`'
                  f' | giveaways `{GIVEAWAY_COUNT}`')


@bot.command(name='avatar')
async def avatar_cmd(ctx, user: discord.User = None):
    user = user or ctx.author
    url = user.avatar.url if user.avatar else user.default_avatar.url
    await ctx.send(url)


@bot.command(name='banner')
async def banner_cmd(ctx, user: discord.User = None):
    user = user or ctx.author
    if user.banner:
        await ctx.send(user.banner.url)
    else:
        await ctx.send('No banner set.')


@bot.command(name='whois')
async def whois_cmd(ctx, user: discord.User = None):
    user = user or ctx.author
    e = bx_embed(str(user))
    e.add_field(name='ID', value=user.id)
    e.add_field(name='Created',
                value=user.created_at.strftime('%Y-%m-%d'))
    e.add_field(name='Bot', value=str(user.bot))
    if user.avatar:
        e.set_thumbnail(url=user.avatar.url)
    await ctx.send(embed=e)


@bot.command(name='serverinfo')
async def serverinfo_cmd(ctx):
    g = ctx.guild
    if not g:
        return await ctx.send('Not in a server.')
    e = bx_embed(g.name)
    e.add_field(name='Members', value=g.member_count)
    e.add_field(name='Owner', value=f'<@{g.owner_id}>')
    e.add_field(name='Channels', value=len(g.channels))
    e.add_field(name='Roles', value=len(g.roles))
    e.add_field(name='Boost', value=f'Level {g.premium_tier}')
    e.add_field(name='Created',
                value=g.created_at.strftime('%Y-%m-%d'))
    if g.icon:
        e.set_thumbnail(url=g.icon.url)
    await ctx.send(embed=e)


@bot.command(name='guildicon')
async def guildicon_cmd(ctx):
    if ctx.guild and ctx.guild.icon:
        await ctx.send(ctx.guild.icon.url)
    else:
        await ctx.send('No icon.')


@bot.command(name='credits')
async def credits_cmd(ctx):
    e = bx_embed('Credits',
        '**Byte X** reversed the entire Nighty PyArmor:\n'
        '- 3 cipher tiers cracked\n'
        '- Opcode substitution reversed\n'
        '- Auth endpoint captured\n'
        '- 771/771 sections recovered\n'
        '- 62k lines of fake updates cleaned\n\n'
        'Credits: **Byte X / gang.baby**\n'
        'Or get mogged.', 0x000000)
    await ctx.send(embed=e)


@bot.command(name='alias')
async def alias_cmd(ctx, action='', old='', *, new=''):
    if action == 'add' and old and new:
        ALIASES[old] = new
        _save('aliases.json', ALIASES)
        await ctx.send(f'`{old}` -> `{new}`')
    elif action == 'remove' and old:
        ALIASES.pop(old, None)
        _save('aliases.json', ALIASES)
        await ctx.send(f'Removed `{old}`')
    elif action == 'list':
        if ALIASES:
            await ctx.send('\n'.join(
                f'`{k}` -> `{v}`' for k, v in ALIASES.items()))
        else:
            await ctx.send('No aliases.')


@bot.command(name='remind')
async def remind_cmd(ctx, seconds: int = 0, *, reminder=''):
    if seconds <= 0 or not reminder:
        return await ctx.send(
            f'Usage: `{PREFIX}remind <seconds> <text>`')
    REMINDERS.append({'t': time.time() + seconds,
                      'text': reminder, 'ch': ctx.channel.id})
    _save('reminders.json', REMINDERS)
    await ctx.send(f'Reminder set for {seconds}s')


@bot.command(name='time')
async def time_cmd(ctx):
    await ctx.send(
        f' `{datetime.now().strftime("%H:%M:%S")}` '
        f'`{datetime.now().strftime("%Y-%m-%d")}`')


@bot.command(name='calculate')
async def calc_cmd(ctx, *, expr=''):
    if not expr:
        return await ctx.send(f'Usage: `{PREFIX}calculate <math>`')
    try:
        expr = re.sub(r'[^0-9+\-*/().% ]', '', expr)
        result = eval(expr)
        await ctx.send(f'`{expr}` = **{result}**')
    except Exception as e:
        await ctx.send(f'Error: `{e}`')


@bot.command(name='random')
async def random_cmd(ctx, lo: int = 1, hi: int = 100):
    await ctx.send(f'**{random.randint(lo, hi)}**')


@bot.command(name='coinflip')
async def coinflip_cmd(ctx):
    await ctx.send(f'**{random.choice(["Heads", "Tails"])}**')


@bot.command(name='roll')
async def roll_cmd(ctx, sides: int = 6):
    await ctx.send(f' **{random.randint(1, sides)}** (d{sides})')


@bot.command(name='8ball')
async def eightball_cmd(ctx, *, question=''):
    responses = [
        'It is certain', 'It is decidedly so', 'Without a doubt',
        'Yes definitely', 'You may rely on it',
        'As I see it, yes', 'Most likely', 'Outlook good',
        'Yes', 'Signs point to yes', 'Reply hazy try again',
        'Ask again later', 'Better not tell you now',
        'Cannot predict now', 'Concentrate and ask again',
        'Don\'t count on it', 'My reply is no',
        'My sources say no', 'Outlook not so good',
        'Very doubtful']
    await ctx.send(f'**{random.choice(responses)}**')


@bot.command(name='choose')
async def choose_cmd(ctx, *, options=''):
    if not options:
        return await ctx.send(f'Usage: `{PREFIX}choose opt1|opt2|...`')
    opts = [o.strip() for o in options.split('|')]
    await ctx.send(f'I choose **{random.choice(opts)}**')


@bot.command(name='rate')
async def rate_cmd(ctx, *, thing=''):
    if not thing:
        return await ctx.send(f'Usage: `{PREFIX}rate <thing>`')
    score = random.randint(0, 10)
    bar = '\u2581' * score + '\u2591' * (10 - score)
    await ctx.send(f'**{thing}**: `{bar}` **{score}/10**')


@bot.command(name='password')
async def password_cmd(ctx, length: int = 16):
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    pw = ''.join(random.choice(chars) for _ in range(length))
    await ctx.send(f'`{pw}`')


# ============================================================
#  TROLLING
# ============================================================
@bot.command(name='hypesquad')
async def hypesquad_cmd(ctx, house=''):
    houses = {'bravery': 1, 'brilliance': 2, 'balance': 3}
    if house.lower() not in houses:
        return await ctx.send('bravery/brilliance/balance')
    await bot.http.change_hypesquad_house(houses[house.lower()])
    await ctx.send(f'**{house.title()}**')


@bot.command(name='embed')
async def embed_cmd(ctx, *, json_str=''):
    if not json_str:
        return await ctx.send(f'Usage: `{PREFIX}embed {{"title":"hi"}}`')
    try:
        await ctx.send(embed=discord.Embed.from_dict(
            json.loads(json_str)))
    except json.JSONDecodeError as e:
        await ctx.send(f'`{e}`')


@bot.command(name='dm')
async def dm_cmd(ctx, user: discord.User, *, message=''):
    if not message:
        return await ctx.send(f'Usage: `{PREFIX}dm @user message`')
    try:
        await user.send(message)
        await ctx.send(f'Sent to {user}')
    except discord.Forbidden:
        await ctx.send(f'{user} has DMs closed')


@bot.command(name='massdm')
async def massdm_cmd(ctx, *, message=''):
    if not message:
        return await ctx.send(f'Usage: `{PREFIX}massdm message`')
    sent = 0
    for friend in bot.friends:
        try:
            await friend.send(message)
            sent += 1
            await asyncio.sleep(1.5)
        except Exception:
            pass
    await ctx.send(f'Sent to {sent} friends')


@bot.command(name='purge')
async def purge_cmd(ctx, count: int = 10):
    if count > 100:
        count = 100
    deleted = 0
    async for msg in ctx.channel.history(limit=300):
        if msg.author.id == bot.user.id:
            await msg.delete()
            deleted += 1
            if deleted >= count:
                break
            await asyncio.sleep(0.4)
    log.info(f'Purged {deleted}')


@bot.command(name='spam')
async def spam_cmd(ctx, count: int = 5, *, message=''):
    if not message or count > 20:
        return await ctx.send(f'Usage: `{PREFIX}spam <1-20> message`')
    for _ in range(min(count, 20)):
        await ctx.send(message)
        await asyncio.sleep(0.7)


@bot.command(name='ghostping')
async def ghostping_cmd(ctx, user: discord.User):
    msg = await ctx.send(f'{user.mention}')
    await msg.delete()


@bot.command(name='quickdelete')
async def quickdelete_cmd(ctx, delay: int = 3, *, message=''):
    if not message:
        return
    msg = await ctx.send(message)
    await asyncio.sleep(delay)
    await msg.delete()


@bot.command(name='fakemention')
async def fakemention_cmd(ctx, user: discord.User):
    await ctx.send(
        f'||{user.mention}|| you didn\'t see anything')


@bot.command(name='react')
async def react_cmd(ctx, message_id: int = 0, emoji=''):
    if not message_id or not emoji:
        return await ctx.send(
            f'Usage: `{PREFIX}react <message_id> <emoji>`')
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.add_reaction(emoji)
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='unreact')
async def unreact_cmd(ctx, message_id: int = 0, emoji=''):
    if not message_id or not emoji:
        return await ctx.send(
            f'Usage: `{PREFIX}unreact <msg_id> <emoji>`')
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.remove_reaction(emoji, ctx.guild.me or bot.user)
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='poll')
async def poll_cmd(ctx, *, question=''):
    if not question:
        return await ctx.send(f'Usage: `{PREFIX}poll question`')
    msg = await ctx.send(embed=bx_embed('Poll', f'**{question}**'))
    await msg.add_reaction('\U0001F44D')
    await msg.add_reaction('\U0001F44E')


@bot.command(name='say')
async def say_cmd(ctx, *, text=''):
    if text:
        await ctx.send(text)


@bot.command(name='echo')
async def echo_cmd(ctx, *, text=''):
    if text:
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send(text)


# ============================================================
#  TEXT FORMATTING
# ============================================================
@bot.command(name='clap')
async def clap_cmd(ctx, *, text=''):
    if text:
        await ctx.send(' '.join(word + ' \U0001F44F'
                     for word in text.split()))


@bot.command(name='sarcasm')
async def sarcasm_cmd(ctx, *, text=''):
    if text:
        await ctx.send(''.join(
            c.upper() if i % 2 else c.lower()
            for i, c in enumerate(text)))


@bot.command(name='vaporwave')
async def vaporwave_cmd(ctx, *, text=''):
    VAPOR = str.maketrans(
        'abcdefghijklmnopqrstuvwxyz',
        '\uff41\uff42\uff43\uff44\uff45\uff46\uff47\uff48\uff49'
        '\uff4a\uff4b\uff4c\uff4d\uff4e\uff4f\uff50\uff51\uff52'
        '\uff53\uff54\uff55\uff56\uff57\uff58\uff59\uff5a')
    if text:
        await ctx.send(text.translate(VAPOR))


@bot.command(name='bold')
async def bold_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'**{text}**')


@bot.command(name='italic')
async def italic_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'*{text}*')


@bot.command(name='underline')
async def underline_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'__{text}__')


@bot.command(name='strike')
async def strike_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'~~{text}~~')


@bot.command(name='spoiler')
async def spoiler_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'||{text}||')


@bot.command(name='code')
async def code_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'```\n{text}\n```')


@bot.command(name='reverse')
async def reverse_cmd(ctx, *, text=''):
    if text:
        await ctx.send(text[::-1])


@bot.command(name='upper')
async def upper_cmd(ctx, *, text=''):
    if text:
        await ctx.send(text.upper())


@bot.command(name='lower')
async def lower_cmd(ctx, *, text=''):
    if text:
        await ctx.send(text.lower())


@bot.command(name='count')
async def count_cmd(ctx, *, text=''):
    if text:
        words = len(text.split())
        chars = len(text)
        await ctx.send(
            f'`{words}` words, `{chars}` characters')


@bot.command(name='morse')
async def morse_cmd(ctx, *, text=''):
    MORSE = {'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..',
             'e': '.', 'f': '..-.', 'g': '--.', 'h': '....',
             'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
             'm': '--', 'n': '-.', 'o': '---', 'p': '.--.',
             'q': '--.-', 'r': '.-.', 's': '...', 't': '-',
             'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
             'y': '-.--', 'z': '--..', '0': '-----',
             '1': '.----', '2': '..---', '3': '...--',
             '4': '....-', '5': '.....', '6': '-....',
             '7': '--...', '8': '---..', '9': '----.'}
    REV = {v: k for k, v in MORSE.items()}
    if not text:
        return
    if '.' in text or '-' in text:
        decoded = ' '.join(
            ''.join(REV.get(c, '?') for c in w.split())
            for w in text.split(' / '))
        await ctx.send(f'`{decoded}`')
    else:
        encoded = ' / '.join(
            ' '.join(MORSE.get(c, '') for c in w)
            for w in text.lower().split())
        await ctx.send(f'`{encoded}`')


@bot.command(name='translate')
async def translate_cmd(ctx, *, text=''):
    if not text or not requests:
        return await ctx.send(f'Usage: `{PREFIX}translate <text>`')
    try:
        r = requests.get(
            'https://translate.googleapis.com/translate_a/single',
            params={'client': 'gtx', 'sl': 'auto', 'tl': 'en',
                    'dt': 't', 'q': text}, timeout=10)
        result = ''.join(p[0] for p in r.json()[0])
        await ctx.send(result)
    except Exception as e:
        await ctx.send(f'`{e}`')


# ============================================================
#  SPOTIFY
# ============================================================
def _spotify_token():
    if not requests:
        return None
    try:
        r = requests.get(
            'https://discord.com/api/v9/users/@me/connections',
            headers={'Authorization': TOKEN})
        for c in r.json():
            if c.get('type') == 'spotify':
                return c.get('access_token')
    except Exception:
        pass
    return None


@bot.command(name='spotify')
async def spotify_cmd(ctx):
    token = _spotify_token()
    if not token:
        return await ctx.send('No Spotify connection.')
    try:
        r = requests.get('https://api.spotify.com/v1/me/player',
                        headers={'Authorization': f'Bearer {token}'})
        if r.status_code != 200:
            return await ctx.send('Not playing.')
        track = r.json().get('item', {})
        artists = ', '.join(
            a['name'] for a in track.get('artists', []))
        await ctx.send(embed=bx_embed(
            'Now Playing',
            f'**{track.get("name", "?")}**\nby {artists}',
            0x1DB954))
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='play')
async def play_cmd(ctx):
    token = _spotify_token()
    if not token:
        return await ctx.send('No Spotify.')
    requests.put('https://api.spotify.com/v1/me/player/pause',
                 headers={'Authorization': f'Bearer {token}'})
    await ctx.send('Toggled')


@bot.command(name='skip')
async def skip_cmd(ctx):
    token = _spotify_token()
    if not token:
        return await ctx.send('No Spotify.')
    requests.post('https://api.spotify.com/v1/me/player/next',
                  headers={'Authorization': f'Bearer {token}'})
    await ctx.send('Skipped')


@bot.command(name='queue')
async def queue_cmd(ctx, *, song=''):
    if not song:
        return await ctx.send(f'Usage: `{PREFIX}queue <song>`')
    token = _spotify_token()
    if not token:
        return await ctx.send('No Spotify.')
    try:
        if 'spotify:' in song:
            uri = song
        else:
            r = requests.get(
                'https://api.spotify.com/v1/search',
                params={'q': song, 'type': 'track', 'limit': 1},
                headers={'Authorization': f'Bearer {token}'})
            tracks = r.json().get('tracks', {}).get('items', [])
            if not tracks:
                return await ctx.send('Not found.')
            uri = tracks[0]['uri']
        requests.post(
            'https://api.spotify.com/v1/me/player/queue',
            params={'uri': uri},
            headers={'Authorization': f'Bearer {token}'})
        await ctx.send('Queued')
    except Exception as e:
        await ctx.send(f'`{e}`')


# ============================================================
#  RPC / PRESENCE
# ============================================================
@bot.command(name='rpc')
async def rpc_cmd(ctx, *, details=''):
    parts = details.split('|') if details else ['', '']
    d = parts[0].strip()
    s = parts[1].strip() if len(parts) > 1 else ''
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=d or 'Byte X', state=s))
    await ctx.send(f'**{d}**')


@bot.command(name='stream')
async def stream_cmd(ctx, *, title=''):
    await bot.change_presence(
        activity=discord.Streaming(
            name=title or 'Byte X',
            url='https://twitch.tv/.'))
    await ctx.send(f'Streaming: **{title}**')


@bot.command(name='rpcoff')
async def rpcoff_cmd(ctx):
    await bot.change_presence(activity=None)
    await ctx.send('Cleared')


@bot.command(name='rpcpreset')
async def rpcpreset_cmd(ctx, action='', name='', *, value=''):
    if action == 'save' and name:
        RPC_PRESETS[name] = value or 'Playing something'
        _save('rpc_presets.json', RPC_PRESETS)
        await ctx.send(f'Saved `{name}`')
    elif action == 'load' and name in RPC_PRESETS:
        await rpc_cmd(ctx, details=RPC_PRESETS[name])
    elif action == 'delete' and name:
        RPC_PRESETS.pop(name, None)
        _save('rpc_presets.json', RPC_PRESETS)
        await ctx.send(f'Deleted `{name}`')
    elif action == 'list':
        if RPC_PRESETS:
            await ctx.send('\n'.join(
                f'`{k}`: {v}' for k, v in RPC_PRESETS.items()))
        else:
            await ctx.send('No presets.')
    else:
        await ctx.send('save/load/delete/list')


@bot.command(name='cycle')
async def cycle_cmd(ctx, action='', *, statuses=''):
    global CYCLE_STATUSES, CYCLE_TASK
    if action == 'on' and statuses:
        CYCLE_STATUSES = [s.strip()
                          for s in statuses.split('|')]
        if CYCLE_TASK:
            CYCLE_TASK.cancel()
        CYCLE_TASK = bot.loop.create_task(
            _cycle_statuses())
        await ctx.send(f'Cycling {len(CYCLE_STATUSES)} statuses')
    elif action == 'off':
        if CYCLE_TASK:
            CYCLE_TASK.cancel()
            CYCLE_TASK = None
        await ctx.send('Cycling stopped')
    else:
        await ctx.send(f'`{PREFIX}cycle on status1|status2|...`')


async def _cycle_statuses():
    global CYCLE_INDEX
    while True:
        await bot.change_presence(
            activity=discord.Game(name=CYCLE_STATUSES[CYCLE_INDEX]))
        CYCLE_INDEX = (CYCLE_INDEX + 1) % len(CYCLE_STATUSES)
        await asyncio.sleep(10)


# ============================================================
#  AUTOMATION
# ============================================================
@bot.command(name='afk')
async def afk_cmd(ctx, *, message=''):
    global AFK, AFK_SINCE, AFK_MESSAGE
    if AFK:
        AFK = False
        AFK_SINCE = None
        await ctx.send(f'Welcome back! {SNIPE_COUNT} nitro while away')
    else:
        AFK = True
        AFK_SINCE = datetime.now()
        if message:
            AFK_MESSAGE = message
        await ctx.send(f'AFK: {AFK_MESSAGE}')


@bot.command(name='autoreact')
async def autoreact_cmd(ctx, emoji=''):
    global AUTO_REACT_ENABLED, AUTO_REACT_EMOJI
    if emoji:
        AUTO_REACT_EMOJI = emoji
        AUTO_REACT_ENABLED = True
        await ctx.send(f'Auto-react: {emoji}')
    elif AUTO_REACT_ENABLED:
        AUTO_REACT_ENABLED = False
        await ctx.send('Auto-react off')
    else:
        AUTO_REACT_EMOJI = AUTO_REACT_EMOJI or '\U0001F44D'
        AUTO_REACT_ENABLED = True
        await ctx.send(f'Auto-react: {AUTO_REACT_EMOJI}')


@bot.command(name='keyword')
async def keyword_cmd(ctx, action='', keyword='', *, response=''):
    if action == 'add' and keyword and response:
        KEYWORD_RESPONSES[keyword.lower()] = response
        await ctx.send(f'`{keyword}` -> `{response[:50]}`')
    elif action == 'remove' and keyword:
        KEYWORD_RESPONSES.pop(keyword.lower(), None)
        await ctx.send(f'Removed `{keyword}`')
    elif action == 'list':
        if KEYWORD_RESPONSES:
            await ctx.send('\n'.join(
                f'`{k}` -> `{v[:40]}`'
                for k, v in KEYWORD_RESPONSES.items()))
        else:
            await ctx.send('No keywords.')
    else:
        await ctx.send('add/remove/list')


@bot.command(name='nitro')
async def nitro_cmd(ctx):
    e = bx_embed('Nitro Sniper',
                 f'Status: **Always on**\n'
                 f'Sniped: **{SNIPE_COUNT}**\n'
                 f'Webhook: {NITRO_WEBHOOK or "none"}\n\n'
                 f'*The sniper from Nighty, minus the paywall.*')
    await ctx.send(embed=e)


@bot.command(name='givesnipe')
async def givesnipe_cmd(ctx):
    await ctx.send(f'Giveaway joiner: **Always on** '
                  f'(joined {GIVEAWAY_COUNT})')


# ============================================================
#  STATUS / PRESENCE
# ============================================================
@bot.command(name='dnd')
async def dnd_cmd(ctx):
    await bot.change_presence(status=discord.Status.dnd)
    await ctx.send('Do Not Disturb')


@bot.command(name='idle')
async def idle_cmd(ctx):
    await bot.change_presence(status=discord.Status.idle)
    await ctx.send('Idle')


@bot.command(name='online')
async def online_cmd(ctx):
    await bot.change_presence(status=discord.Status.online)
    await ctx.send('Online')


@bot.command(name='invisible')
async def invisible_cmd(ctx):
    await bot.change_presence(status=discord.Status.invisible)
    await ctx.send('Invisible')


@bot.command(name='setstatus')
async def setstatus_cmd(ctx, *, status=''):
    if not status:
        return await ctx.send(f'Usage: `{PREFIX}setstatus <text>`')
    await bot.change_presence(activity=discord.CustomActivity(name=status))
    await ctx.send(f'Status: **{status}**')


@bot.command(name='setabout')
async def setabout_cmd(ctx, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}setabout <text>`')
    await bot.user.edit(bio=text)
    await ctx.send('About me updated')


@bot.command(name='setpronouns')
async def setpronouns_cmd(ctx, *, pronouns=''):
    if not pronouns:
        return await ctx.send(f'Usage: `{PREFIX}setpronouns <text>`')
    await bot.http.edit_profile({'pronouns': pronouns})
    await ctx.send(f'Pronouns: **{pronouns}**')


# ============================================================
#  SERVER INFO
# ============================================================
@bot.command(name='channelinfo')
async def channelinfo_cmd(ctx, channel: discord.TextChannel = None):
    ch = channel or ctx.channel
    e = bx_embed(f'#{ch.name}')
    e.add_field(name='ID', value=ch.id)
    e.add_field(name='Type', value=str(ch.type))
    e.add_field(name='NSFW', value=str(getattr(ch, 'nsfw', False)))
    e.add_field(name='Slowmode', value=f'{ch.slowmode_delay}s')
    if ch.topic:
        e.add_field(name='Topic', value=ch.topic[:200], inline=False)
    await ctx.send(embed=e)


@bot.command(name='rolelist')
async def rolelist_cmd(ctx):
    if not ctx.guild:
        return
    roles = [r.mention for r in reversed(ctx.guild.roles)
             if r.name != '@everyone'][:30]
    await ctx.send(' '.join(roles))


@bot.command(name='botlist')
async def botlist_cmd(ctx):
    if not ctx.guild:
        return
    bots = [f'`{m.name}`' for m in ctx.guild.members if m.bot][:20]
    if bots:
        await ctx.send(f'**Bots ({len(bots)}):** ' + ' '.join(bots))
    else:
        await ctx.send('No bots.')


@bot.command(name='inrole')
async def inrole_cmd(ctx, *, role_name=''):
    if not role_name or not ctx.guild:
        return await ctx.send(f'Usage: `{PREFIX}inrole <role>`')
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send('Role not found.')
    members = [f'`{m.name}`' for m in role.members][:20]
    await ctx.send(f'**{role.name} ({len(role.members)}):** ' + ' '.join(members))


@bot.command(name='mods')
async def mods_cmd(ctx):
    if not ctx.guild:
        return
    mods = [f'`{m.name}`' for m in ctx.guild.members
            if m.guild_permissions.kick_members
            and not m.bot][:15]
    await ctx.send(f'**Mods:** ' + ' '.join(mods) if mods else 'None found.')


@bot.command(name='admins')
async def admins_cmd(ctx):
    if not ctx.guild:
        return
    admins = [f'`{m.name}`' for m in ctx.guild.members
              if m.guild_permissions.administrator
              and not m.bot][:15]
    await ctx.send(f'**Admins:** ' + ' '.join(admins) if admins else 'None found.')


@bot.command(name='owner')
async def owner_cmd(ctx):
    if ctx.guild:
        await ctx.send(f'Owner: <@{ctx.guild.owner_id}>')


@bot.command(name='joindate')
async def joindate_cmd(ctx, user: discord.User = None):
    user = user or ctx.author
    member = ctx.guild.get_member(user.id) if ctx.guild else None
    if member and member.joined_at:
        await ctx.send(f'{user} joined {member.joined_at.strftime("%Y-%m-%d %H:%M")}')
    else:
        await ctx.send('Not in this server.')


@bot.command(name='serverlist')
async def serverlist_cmd(ctx):
    guilds = sorted(bot.guilds, key=lambda g: -g.member_count)[:15]
    lines = [f'**{g.name}** ({g.member_count} members)' for g in guilds]
    await ctx.send('\n'.join(lines))


@bot.command(name='boost')
async def boost_cmd(ctx):
    if not ctx.guild:
        return
    g = ctx.guild
    await ctx.send(f'Boost level: **{g.premium_tier}** | '
                  f'Boosts: **{g.premium_subscription_count}**')


@bot.command(name='pins')
async def pins_cmd(ctx):
    pinned = await ctx.channel.pins()
    if pinned:
        await ctx.send('\n'.join(
            f'[Jump]({m.jump_url}) - {m.content[:50]}' for m in pinned[:5]))
    else:
        await ctx.send('No pinned messages.')


@bot.command(name='invite')
async def invite_cmd(ctx):
    try:
        invite = await ctx.channel.create_invite(max_age=86400)
        await ctx.send(str(invite))
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='invites')
async def invites_cmd(ctx):
    if not ctx.guild:
        return
    invites = await ctx.guild.invites()
    mine = [i for i in invites if i.inviter.id == bot.user.id]
    uses = sum(i.uses for i in mine)
    await ctx.send(f'Your invites: **{len(mine)}** links, **{uses}** uses')


# ============================================================
#  MESSAGING
# ============================================================
@bot.command(name='typing')
async def typing_cmd(ctx, seconds: int = 5):
    async with ctx.channel.typing():
        await asyncio.sleep(min(seconds, 30))
    await ctx.send('Done typing.')


@bot.command(name='forward')
async def forward_cmd(ctx, channel: discord.TextChannel, message_id: int):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        if msg.content:
            await channel.send(msg.content)
        if msg.embeds:
            for emb in msg.embeds:
                await channel.send(embed=emb)
        if msg.attachments:
            for att in msg.attachments:
                await channel.send(att.url)
        await ctx.send('Forwarded.')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='quote')
async def quote_cmd(ctx, message_id: int):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        e = bx_embed(f'{msg.author} said:',
                     msg.content[:1000])
        await ctx.send(embed=e)
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='pin')
async def pin_cmd(ctx, message_id: int):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.pin()
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='unpin')
async def unpin_cmd(ctx, message_id: int):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.unpin()
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='webhook')
async def webhook_cmd(ctx, url='', *, message=''):
    if not url.startswith('https://') or not message:
        return await ctx.send(f'Usage: `{PREFIX}webhook <url> <message>`')
    if requests:
        try:
            r = requests.post(url, json={'content': message})
            await ctx.send(f'`{r.status_code}`')
        except Exception as e:
            await ctx.send(f'`{e}`')


@bot.command(name='read')
async def read_cmd(ctx):
    await ctx.message.ack()


# ============================================================
#  SOCIAL
# ============================================================
@bot.command(name='unfriend')
async def unfriend_cmd(ctx, user: discord.User):
    await user.remove_friend()
    await ctx.send(f'Removed {user}')


@bot.command(name='block')
async def block_cmd(ctx, user: discord.User):
    await user.block()
    await ctx.send(f'Blocked {user}')


@bot.command(name='unblock')
async def unblock_cmd(ctx, user: discord.User):
    await user.unblock()
    await ctx.send(f'Unblocked {user}')


@bot.command(name='connections')
async def connections_cmd(ctx):
    r = await bot.http.get_connections()
    if r:
        lines = [f'**{c["type"]}**: {c.get("name", "?")}' for c in r]
        await ctx.send('\n'.join(lines))
    else:
        await ctx.send('No connections.')


@bot.command(name='email')
async def email_cmd(ctx):
    u = await bot.http.get_me()
    email = u.get('email', 'None')
    await ctx.send(f'`{email}`')


@bot.command(name='nitroinfo')
async def nitroinfo_cmd(ctx):
    u = await bot.http.get_me()
    pt = u.get('premium_type', 0)
    types = {0: 'None', 1: 'Nitro Classic', 2: 'Nitro', 3: 'Nitro Basic'}
    await ctx.send(f'**{types.get(pt, pt)}**')


# ============================================================
#  ENCODING / DECODING
# ============================================================
@bot.command(name='base64')
async def base64_cmd(ctx, mode='e', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}base64 e/d <text>`')
    try:
        if mode == 'e':
            result = base64.b64encode(text.encode()).decode()
        else:
            result = base64.b64decode(text).decode()
        await ctx.send(f'`{result}`')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='hex')
async def hex_cmd(ctx, mode='e', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}hex e/d <text>`')
    try:
        if mode == 'e':
            result = text.encode().hex()
        else:
            result = bytes.fromhex(text).decode()
        await ctx.send(f'`{result}`')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='binary')
async def binary_cmd(ctx, mode='e', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}binary e/d <text>`')
    try:
        if mode == 'e':
            result = ' '.join(format(ord(c), '08b') for c in text)
        else:
            result = ''.join(chr(int(b, 2)) for b in text.split())
        await ctx.send(f'`{result}`')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='url')
async def url_cmd(ctx, mode='e', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}url e/d <text>`')
    from urllib.parse import quote, unquote
    result = quote(text) if mode == 'e' else unquote(text)
    await ctx.send(f'`{result}`')


@bot.command(name='rot13')
async def rot13_cmd(ctx, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}rot13 <text>`')
    import codecs
    result = codecs.encode(text, 'rot13')
    await ctx.send(f'`{result}`')


@bot.command(name='hash')
async def hash_cmd(ctx, algo='md5', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}hash <md5/sha1/sha256> <text>`')
    try:
        h = hashlib.new(algo)
        h.update(text.encode())
        await ctx.send(f'`{algo}: {h.hexdigest()}`')
    except Exception:
        await ctx.send('Use md5, sha1, or sha256')


@bot.command(name='uuid')
async def uuid_cmd(ctx):
    import uuid as uuid_mod
    await ctx.send(f'`{uuid_mod.uuid4()}`')


@bot.command(name='snowflake')
async def snowflake_cmd(ctx, snowflake: int = 0):
    if not snowflake:
        return await ctx.send(f'Usage: `{PREFIX}snowflake <id>`')
    ts = (snowflake >> 22) + 1420070400000
    dt = datetime.fromtimestamp(ts / 1000)
    await ctx.send(f'`{dt.strftime("%Y-%m-%d %H:%M:%S")} (worker: {(snowflake & 0x3E0000) >> 17}, '
                  f'pid: {(snowflake & 0x1F000) >> 12}, incr: {snowflake & 0xFFF})`')


@bot.command(name='timestamp')
async def timestamp_cmd(ctx, ts: float = 0):
    if ts:
        dt = datetime.fromtimestamp(ts)
        await ctx.send(f'`{dt.strftime("%Y-%m-%d %H:%M:%S")}`')
    else:
        await ctx.send(f'`{int(time.time())}`')


# ============================================================
#  MEDIA / UTILITY
# ============================================================
@bot.command(name='gif')
async def gif_cmd(ctx, *, query=''):
    if not query or not requests:
        return await ctx.send(f'Usage: `{PREFIX}gif <search>`')
    try:
        r = requests.get(
            'https://api.giphy.com/v1/gifs/random',
            params={'api_key': 'dc6zaTOxFJmzC', 'tag': query},
            timeout=10)
        url = r.json().get('data', {}).get('image_url')
        if url:
            await ctx.send(url)
        else:
            await ctx.send('Not found.')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='imgur')
async def imgur_cmd(ctx, url=''):
    if not url:
        return await ctx.send(f'Usage: `{PREFIX}imgur <image_url>`')
    await ctx.send('(imgur upload requires an API key, just use the URL directly)')


@bot.command(name='qr')
async def qr_cmd(ctx, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}qr <text>`')
    from urllib.parse import quote as _q
    await ctx.send(f'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={_q(text)}')


@bot.command(name='addreactions')
async def addreactions_cmd(ctx, message_id: int = 0, *, emojis=''):
    if not message_id or not emojis:
        return await ctx.send(f'Usage: `{PREFIX}addreactions <msg_id> <emoji1 emoji2...>`')
    try:
        msg = await ctx.channel.fetch_message(message_id)
        for emoji in emojis.split()[:10]:
            await msg.add_reaction(emoji)
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='clearreactions')
async def clearreactions_cmd(ctx, message_id: int = 0):
    if not message_id:
        return await ctx.send(f'Usage: `{PREFIX}clearreactions <msg_id>`')
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.clear_reactions()
    except Exception as e:
        await ctx.send(f'`{e}`')


# ============================================================
#  EXTRA TROLLING
# ============================================================
@bot.command(name='empty')
async def empty_cmd(ctx):
    await ctx.send('​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​')


@bot.command(name='spacer')
async def spacer_cmd(ctx, count: int = 10):
    count = min(count, 50)
    await ctx.send('\u200b\n' * count)


@bot.command(name='multiline')
async def multiline_cmd(ctx, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}multiline line1|line2|...`')
    lines = text.split('|')
    await ctx.send('\n'.join(lines))


@bot.command(name='fakemessage')
async def fakemessage_cmd(ctx, user: discord.User, *, message=''):
    if not message:
        return await ctx.send(f'Usage: `{PREFIX}fakemessage @user text`')
    e = bx_embed('', f'**{user.name}**: {message}')
    try:
        e.set_author(name=str(user), icon_url=user.avatar.url if user.avatar else '')
    except Exception:
        pass
    await ctx.send(embed=e)


# ============================================================
#  PRESENCE VARIANTS
# ============================================================
@bot.command(name='listening')
async def listening_cmd(ctx, *, text=''):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name=text or 'Byte X'))
    await ctx.send(f'Listening to: **{text}**')


@bot.command(name='watching')
async def watching_cmd(ctx, *, text=''):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=text or 'Byte X'))
    await ctx.send(f'Watching: **{text}**')


@bot.command(name='competing')
async def competing_cmd(ctx, *, text=''):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.competing,
        name=text or 'Byte X'))
    await ctx.send(f'Competing in: **{text}**')


@bot.command(name='playing')
async def playing_cmd(ctx, *, text=''):
    await bot.change_presence(activity=discord.Game(
        name=text or 'Byte X'))
    await ctx.send(f'Playing: **{text}**')


@bot.command(name='setavatar')
async def setavatar_cmd(ctx, url=''):
    if not url and ctx.message.attachments:
        url = ctx.message.attachments[0].url
    if not url:
        return await ctx.send(f'Usage: `{PREFIX}setavatar <url>`')
    if requests:
        try:
            img = requests.get(url, timeout=10).content
            await bot.user.edit(avatar=img)
            await ctx.send('Avatar updated.')
        except Exception as e:
            await ctx.send(f'`{e}`')


# ============================================================
#  MASS ACTIONS
# ============================================================
@bot.command(name='wipe')
async def wipe_cmd(ctx, count: int = 50):
    count = min(count, 200)
    deleted = 0
    async for msg in ctx.channel.history(limit=500):
        if msg.author.id == bot.user.id:
            await msg.delete()
            deleted += 1
            if deleted >= count:
                break
            await asyncio.sleep(0.3)
    log.info(f'Wiped {deleted} messages')


@bot.command(name='scare')
async def scare_cmd(ctx, user: discord.User, times: int = 5):
    if times > 10:
        times = 10
    for _ in range(times):
        msg = await ctx.send(f'{user.mention}')
        await msg.delete()
        await asyncio.sleep(0.5)


@bot.command(name='slowspam')
async def slowspam_cmd(ctx, count: int = 5, delay: float = 1.0, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}slowspam <n> <delay> <text>`')
    for _ in range(min(count, 30)):
        await ctx.send(text)
        await asyncio.sleep(max(delay, 0.5))


@bot.command(name='friendall')
async def friendall_cmd(ctx):
    if not ctx.guild:
        return
    sent = 0
    for member in ctx.guild.members:
        if member.id == bot.user.id or member.bot:
            continue
        try:
            await member.send_friend_request()
            sent += 1
            await asyncio.sleep(2)
        except Exception:
            pass
        if sent >= 20:
            break
    await ctx.send(f'Sent {sent} friend requests.')


@bot.command(name='autodelete')
async def autodelete_cmd(ctx, seconds: int = 5, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}autodelete <sec> <text>`')
    msg = await ctx.send(text)
    await asyncio.sleep(seconds)
    try:
        await msg.delete()
    except Exception:
        pass


@bot.command(name='typestart')
async def typestart_cmd(ctx):
    global _typing
    _typing = True
    async def _do_typing():
        while _typing:
            try:
                await ctx.channel.trigger_typing()
            except Exception:
                pass
            await asyncio.sleep(8)
    bot.loop.create_task(_do_typing())
    await ctx.send('Typing loop started.')


@bot.command(name='typestop')
async def typestop_cmd(ctx):
    global _typing
    _typing = False
    await ctx.send('Typing loop stopped.')


# ============================================================
#  QUICK STATS
# ============================================================
@bot.command(name='guildcount')
async def guildcount_cmd(ctx):
    await ctx.send(f'In **{len(bot.guilds)}** servers.')


@bot.command(name='friendcount')
async def friendcount_cmd(ctx):
    await ctx.send(f'**{len(bot.friends)}** friends.')


@bot.command(name='blockcount')
async def blockcount_cmd(ctx):
    await ctx.send(f'**{len([r for r in bot.relationships if r.type == discord.RelationshipType.blocked])}** blocked users.')


@bot.command(name='pending')
async def pending_cmd(ctx):
    pending = [f'`{r.user}`' for r in [r for r in bot.relationships if r.type == discord.RelationshipType.incoming_request]]
    if pending:
        await ctx.send(f'Pending: ' + ' '.join(pending[:10]))
    else:
        await ctx.send('No pending requests.')


@bot.command(name='relationship')
async def relationship_cmd(ctx, user: discord.User):
    rel = user.relationship
    types = {discord.RelationshipType.friend: 'Friend',
             discord.RelationshipType.blocked: 'Blocked',
             discord.RelationshipType.incoming_request: 'Incoming',
             discord.RelationshipType.outgoing_request: 'Outgoing'}
    if rel:
        await ctx.send(f'**{user}**: {types.get(rel.type, rel.type)}')
    else:
        await ctx.send(f'**{user}**: None.')


# ============================================================
#  NOTES
# ============================================================
NOTES_FILE = DATA_DIR / 'notes.json'
NOTES = _load('notes.json')

@bot.command(name='note')
async def note_cmd(ctx, user: discord.User, *, note=''):
    if not note:
        NOTES.pop(str(user.id), None)
        _save('notes.json', NOTES)
        return await ctx.send('Note removed.')
    NOTES[str(user.id)] = {'name': str(user), 'note': note}
    _save('notes.json', NOTES)
    await ctx.send(f'Note saved for {user}.')


@bot.command(name='notes')
async def notes_cmd(ctx):
    if NOTES:
        lines = [f'**{v["name"]}**: {v["note"][:50]}' for v in NOTES.values()]
        await ctx.send('\n'.join(lines[:15]))
    else:
        await ctx.send('No notes saved.')


# ============================================================
#  EMOJI / STICKER INFO
# ============================================================
@bot.command(name='emojiinfo')
async def emojiinfo_cmd(ctx, emoji=''):
    m = re.search(r'<a?:(\w+):(\d+)>', emoji)
    if not m:
        return await ctx.send(f'Usage: `{PREFIX}emojiinfo :emoji:`')
    name, eid = m.groups()
    animated = emoji.startswith('<a:')
    ext = 'gif' if animated else 'png'
    url = f'https://cdn.discordapp.com/emojis/{eid}.{ext}'
    e = bx_embed(f':{name}:')
    e.add_field(name='Name', value=name)
    e.add_field(name='ID', value=eid)
    e.add_field(name='Animated', value=str(animated))
    e.set_thumbnail(url=url)
    await ctx.send(embed=e)


@bot.command(name='emojidel')
async def emojidel_cmd(ctx, emoji=''):
    if not emoji or not ctx.guild:
        return
    m = re.search(r'<a?:(\w+):(\d+)>', emoji)
    if not m:
        return
    emo = discord.utils.get(ctx.guild.emojis, id=int(m.group(2)))
    if emo:
        try:
            await emo.delete()
            await ctx.send(f'Deleted :{emo.name}:')
        except Exception as e:
            await ctx.send(f'`{e}`')


@bot.command(name='emojirename')
async def emojirename_cmd(ctx, emoji='', new_name=''):
    if not emoji or not new_name or not ctx.guild:
        return
    m = re.search(r'<a?:(\w+):(\d+)>', emoji)
    if not m:
        return
    emo = discord.utils.get(ctx.guild.emojis, id=int(m.group(2)))
    if emo:
        try:
            await emo.edit(name=new_name)
            await ctx.send(f'Renamed to :{new_name}:')
        except Exception as e:
            await ctx.send(f'`{e}`')


@bot.command(name='stickers')
async def stickers_cmd(ctx):
    if not ctx.guild:
        return
    stks = ctx.guild.stickers[:20]
    if stks:
        lines = [f'**{s.name}** - {s.description[:30]}' for s in stks]
        await ctx.send('\n'.join(lines))
    else:
        await ctx.send('No stickers.')


# ============================================================
#  VOICE
# ============================================================
@bot.command(name='voicestate')
async def voicestate_cmd(ctx):
    vs = bot.user.voice
    if vs and vs.channel:
        e = bx_embed(f'In #{vs.channel.name}')
        e.add_field(name='Muted', value=str(vs.self_mute))
        e.add_field(name='Deafened', value=str(vs.self_deaf))
        e.add_field(name='Video', value=str(vs.self_video))
        e.add_field(name='Streaming', value=str(vs.self_stream))
        await ctx.send(embed=e)
    else:
        await ctx.send('Not in voice.')


@bot.command(name='deafen')
async def deafen_cmd(ctx):
    vs = bot.user.voice
    if vs:
        await vs.channel.guild.change_voice_state(
            channel=vs.channel, self_deaf=not vs.self_deaf)
        await ctx.send(f'Deafen: **{not vs.self_deaf}**')
    else:
        await ctx.send('Not in voice.')


@bot.command(name='selfmute')
async def selfmute_cmd(ctx):
    vs = bot.user.voice
    if vs:
        await vs.channel.guild.change_voice_state(
            channel=vs.channel, self_mute=not vs.self_mute)
        await ctx.send(f'Mute: **{not vs.self_mute}**')
    else:
        await ctx.send('Not in voice.')


@bot.command(name='screenshare')
async def screenshare_cmd(ctx):
    vs = bot.user.voice
    if vs and vs.channel:
        from datetime import datetime as _dt
        import time as _time
        await ctx.send(
            f'https://discordapp.com/channels/'
            f'{vs.channel.guild.id}/{vs.channel.id}')
    else:
        await ctx.send('Not in voice.')


@bot.command(name='camera')
async def camera_cmd(ctx):
    vs = bot.user.voice
    if vs:
        await vs.channel.guild.change_voice_state(
            channel=vs.channel, self_video=not vs.self_video)
        await ctx.send(f'Camera: **{not vs.self_video}**')
    else:
        await ctx.send('Not in voice.')


# ============================================================
#  GAMES
# ============================================================
@bot.command(name='rps')
async def rps_cmd(ctx, choice=''):
    choices = ['rock', 'paper', 'scissors']
    if choice.lower() not in choices:
        return await ctx.send('rock/paper/scissors')
    bot_choice = random.choice(choices)
    wins = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    if choice.lower() == bot_choice:
        result = 'Tie!'
    elif wins[choice.lower()] == bot_choice:
        result = 'You win!'
    else:
        result = 'You lose!'
    await ctx.send(f'You: **{choice}** | Me: **{bot_choice}** | {result}')


@bot.command(name='minesweeper')
async def minesweeper_cmd(ctx, size=5, mines=5):
    size = min(size, 8)
    mines = min(mines, size * size // 3)
    grid = [[0] * size for _ in range(size)]
    placed = 0
    while placed < mines:
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        if grid[y][x] != -1:
            grid[y][x] = -1
            placed += 1
    nums = ['\u0030\uFE0F\u20E3', '\u0031\uFE0F\u20E3', '\u0032\uFE0F\u20E3',
            '\u0033\uFE0F\u20E3', '\u0034\uFE0F\u20E3', '\u0035\uFE0F\u20E3',
            '\u0036\uFE0F\u20E3', '\u0037\uFE0F\u20E3', '\u0038\uFE0F\u20E3']
    bomb = '\uD83D\uDCA3'
    board = ''
    for y in range(size):
        for x in range(size):
            if grid[y][x] == -1:
                board += f'||{bomb}||'
            else:
                count = sum(1 for dy in [-1,0,1] for dx in [-1,0,1]
                           if 0 <= y+dy < size and 0 <= x+dx < size
                           and grid[y+dy][x+dx] == -1)
                board += f'||{nums[count]}||'
        board += '\n'
    await ctx.send(board)


@bot.command(name='tictactoe')
async def tictactoe_cmd(ctx):
    board = ['\U0001F7E6'] * 9
    board[random.randint(0, 8)] = '\u274C'
    grid = '\n'.join(''.join(board[i:i+3]) for i in [0, 3, 6])
    await ctx.send(f'```\nTic Tac Toe\n\n{grid}\n```\nUse reactions to play! (coming soon)')


# ============================================================
#  API LOOKUPS (these use free public APIs)
# ============================================================
@bot.command(name='urban')
async def urban_cmd(ctx, *, term=''):
    if not term or not requests:
        return await ctx.send(f'Usage: `{PREFIX}urban <term>`')
    try:
        r = requests.get(
            'https://api.urbandictionary.com/v0/define',
            params={'term': term}, timeout=10)
        results = r.json().get('list', [])
        if results:
            d = results[0]
            e = bx_embed(f'Urban: {term}',
                        d.get('definition', '')[:800], 0xFFFF00)
            e.add_field(name='Example',
                       value=d.get('example', '')[:200] or 'None')
            await ctx.send(embed=e)
        else:
            await ctx.send('Not found.')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='crypto')
async def crypto_cmd(ctx, coin='bitcoin'):
    if not requests:
        return
    try:
        r = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': coin, 'vs_currencies': 'usd'},
            timeout=10)
        data = r.json()
        if coin in data:
            price = data[coin]['usd']
            await ctx.send(f'**{coin.title()}**: `${price:,.2f}`')
        else:
            await ctx.send('Not found. Try: bitcoin, ethereum, dogecoin')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='weather')
async def weather_cmd(ctx, *, city=''):
    if not city or not requests:
        return await ctx.send(f'Usage: `{PREFIX}weather <city>`')
    try:
        r = requests.get(
            f'https://wttr.in/{city}?format=3', timeout=10,
            headers={'User-Agent': 'curl'})
        await ctx.send(f'`{r.text.strip()}`')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='meme')
async def meme_cmd(ctx):
    if not requests:
        return
    try:
        r = requests.get('https://meme-api.com/gimme', timeout=10)
        data = r.json()
        await ctx.send(f'**{data["title"]}**\n{data["url"]}')
    except Exception:
        await ctx.send('API down.')


@bot.command(name='reddit')
async def reddit_cmd(ctx, subreddit='memes'):
    if not requests:
        return
    try:
        r = requests.get(
            f'https://www.reddit.com/r/{subreddit}/random.json',
            headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = r.json()[0]['data']['children'][0]['data']
        await ctx.send(f'**{data["title"]}**\nhttps://reddit.com{data["permalink"]}')
    except Exception:
        await ctx.send('Failed.')


@bot.command(name='cat')
async def cat_cmd(ctx):
    if requests:
        try:
            r = requests.get(
                'https://api.thecatapi.com/v1/images/search',
                timeout=10)
            await ctx.send(r.json()[0]['url'])
        except Exception:
            pass


@bot.command(name='dog')
async def dog_cmd(ctx):
    if requests:
        try:
            r = requests.get('https://random.dog/woof.json', timeout=10)
            await ctx.send(r.json()['url'])
        except Exception:
            pass


@bot.command(name='fox')
async def fox_cmd(ctx):
    if requests:
        try:
            r = requests.get('https://randomfox.ca/floof/', timeout=10)
            await ctx.send(r.json()['image'])
        except Exception:
            pass


@bot.command(name='shibe')
async def shibe_cmd(ctx):
    if requests:
        try:
            r = requests.get(
                'http://shibe.online/api/shibes?count=1', timeout=10)
            await ctx.send(r.json()[0])
        except Exception:
            pass


@bot.command(name='bird')
async def bird_cmd(ctx):
    if requests:
        try:
            r = requests.get('https://some-random-api.ml/img/bird',
                            timeout=10)
            await ctx.send(r.json()['link'])
        except Exception:
            pass


# ============================================================
#  TEXT GENERATORS
# ============================================================
@bot.command(name='supreme')
async def supreme_cmd(ctx, *, text=''):
    if not text:
        return
    from urllib.parse import quote as _q
    await ctx.send(
        f'https://api.supreme.com/api/v1/text/'
        f'?text={_q(text)}&color=red')


@bot.command(name='starwars')
async def starwars_cmd(ctx, *, name=''):
    if not name:
        return
    first = name.split()[0]
    last = name.split()[-1] if len(name.split()) > 1 else ''
    sw_first = {'A': 'Wh', 'B': 'Dh', 'C': 'Ch', 'D': 'Lo', 'E': 'Sh',
                'F': 'Gr', 'G': 'Er', 'H': 'Ch', 'I': 'Zh', 'J': 'Ve',
                'K': 'Ak', 'L': 'Sh', 'M': 'Ul', 'N': 'Gen', 'O': 'Sh',
                'P': 'Ts', 'Q': 'St', 'R': 'Sh', 'S': 'Os', 'T': 'Ts',
                'U': 'Sh', 'V': 'Dv', 'W': 'Wh', 'X': 'Xo', 'Y': 'Yo',
                'Z': 'Zh'}
    sw_last = {'A': 'Ack', 'B': 'Bac', 'C': 'Coc', 'D': 'Dak', 'E': 'Eck',
               'F': 'Fak', 'G': 'Gock', 'H': 'Hack', 'I': 'Ick', 'J': 'Jak',
               'K': 'Kock', 'L': 'Lack', 'M': 'Mack', 'N': 'Nack',
               'O': 'Ock', 'P': 'Pak', 'Q': 'Quak', 'R': 'Rack',
               'S': 'San', 'T': 'Tan', 'U': 'Uck', 'V': 'Vack',
               'W': 'Wack', 'X': 'Xan', 'Y': 'Yack', 'Z': 'Zack'}
    fn = sw_first.get(first[0].upper(), 'Wh') + first[1:].lower()
    ln = (last[0].lower() + sw_last.get(last[-1].upper(), 'ack')
          if last else 'Skywalker')
    await ctx.send(f'**{fn} {ln}**')


@bot.command(name='bandname')
async def bandname_cmd(ctx):
    adjectives = ['crimson', 'electric', 'midnight', 'silent', 'velvet',
                  'neon', 'cosmic', 'broken', 'golden', 'phantom']
    nouns = ['wolves', 'echoes', 'machines', 'ghosts', 'kings',
             'dancers', 'smoke', 'thunder', 'fire', 'diamonds']
    await ctx.send(f'**The {random.choice(adjectives).title()} '
                  f'{random.choice(nouns).title()}**')


@bot.command(name='joke')
async def joke_cmd(ctx):
    if not requests:
        return
    try:
        r = requests.get(
            'https://official-joke-api.appspot.com/random_joke',
            timeout=10)
        d = r.json()
        await ctx.send(f'**{d["setup"]}**\n\n||{d["punchline"]}||')
    except Exception:
        await ctx.send('Why did the programmer quit? '
                      'He didn\'t get arrays.')


@bot.command(name='fact')
async def fact_cmd(ctx):
    if not requests:
        return
    try:
        r = requests.get(
            'https://uselessfacts.jsph.pl/random.json?language=en',
            timeout=10)
        await ctx.send(r.json()['text'])
    except Exception:
        await ctx.send('Honey never spoils.')


@bot.command(name='advice')
async def advice_cmd(ctx):
    if not requests:
        return
    try:
        r = requests.get('https://api.adviceslip.com/advice', timeout=10)
        await ctx.send(r.json()['slip']['advice'])
    except Exception:
        await ctx.send('Just do it.')


@bot.command(name='affirmation')
async def affirmation_cmd(ctx):
    if not requests:
        return
    try:
        r = requests.get('https://www.affirmations.dev/', timeout=10)
        await ctx.send(r.json()['affirmation'])
    except Exception:
        await ctx.send('You are awesome.')


@bot.command(name='showerthought')
async def showerthought_cmd(ctx):
    if not requests:
        return
    try:
        r = requests.get(
            'https://www.reddit.com/r/showerthoughts/random.json',
            headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = r.json()[0]['data']['children'][0]['data']
        await ctx.send(f'*{data["title"]}*')
    except Exception:
        await ctx.send('*If you clean a vacuum cleaner, '
                      'you become the vacuum cleaner.*')


@bot.command(name='unpopular')
async def unpopular_cmd(ctx):
    opinions = [
        'pineapple belongs on pizza',
        'cereal is soup',
        'hot dogs are sandwiches',
        'the toilet paper goes under',
        'bathroom phones are fine',
        'socks with sandals looks good',
        'dark mode is overrated',
        'tabs > spaces',
        'iOS > Android',
        'Twitter was better before',
        'the metric system is confusing',
        'every month needs 30 days',
        'bitwise operators are readable',
        'PHP is a good language',
        'semicolons in JS are unnecessary',
        'AI generated code is fine',
        'selfbots are ethical',
    ]
    await ctx.send(f'*{random.choice(opinions)}*')


# ============================================================
#  WIKI / DICTIONARY
# ============================================================
@bot.command(name='wiki')
async def wiki_cmd(ctx, *, query=''):
    if not query or not requests:
        return await ctx.send(f'Usage: `{PREFIX}wiki <topic>`')
    try:
        r = requests.get(
            'https://en.wikipedia.org/api/rest_v1/page/summary/' + query,
            headers={'User-Agent': 'ByteX/1.0'}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            e = bx_embed(d.get('title', query),
                        d.get('extract', '')[:500])
            await ctx.send(embed=e)
        else:
            await ctx.send('Not found on Wikipedia.')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='dictionary')
async def dictionary_cmd(ctx, *, word=''):
    if not word or not requests:
        return await ctx.send(f'Usage: `{PREFIX}dictionary <word>`')
    try:
        r = requests.get(
            f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}',
            timeout=10)
        if r.status_code == 200:
            data = r.json()[0]
            meanings = data.get('meanings', [])[:3]
            lines = []
            for m in meanings:
                pos = m.get('partOfSpeech', '?')
                defs = m.get('definitions', [])[:2]
                for d in defs:
                    lines.append(f'**{pos}**: {d.get("definition", "")[:150]}')
            if lines:
                await ctx.send('\n'.join(lines))
            else:
                await ctx.send('No definitions found.')
        else:
            await ctx.send('Word not found.')
    except Exception as e:
        await ctx.send(f'`{e}`')


# ============================================================
#  MESSAGE SNIPING
# ============================================================
@bot.command(name='snipe')
async def snipe_cmd(ctx):
    ch_id = ctx.channel.id
    if ch_id in SNIPED_MESSAGES:
        msg = SNIPED_MESSAGES[ch_id]
        e = bx_embed('Sniped',
                     msg['content'] or '(no text)',
                     0xFF0000)
        e.add_field(name='Author', value=msg['author'])
        if msg.get('attachments'):
            e.set_image(url=msg['attachments'])
        await ctx.send(embed=e)
    else:
        await ctx.send('Nothing to snipe.')


@bot.command(name='editsnipe')
async def editsnipe_cmd(ctx):
    ch_id = ctx.channel.id
    if ch_id in EDIT_SNIPED:
        msg = EDIT_SNIPED[ch_id]
        e = bx_embed('Edit Sniped',
                     f'**Before:** {msg["before"]}\n'
                     f'**After:** {msg["after"]}', 0xFFAA00)
        await ctx.send(embed=e)
    else:
        await ctx.send('Nothing to snipe.')


# ============================================================
#  TEXT GENERATORS (the fun ones)
# ============================================================
ZALGO_CHARS = [
    '\u0300\u0301\u0302\u0303\u0304\u0305\u0306\u0307\u0308',
    '\u0316\u0317\u0318\u0319\u031a\u031b\u031c\u031d',
    '\u0348\u0349\u034a\u034b\u034c\u034d\u034e\u034f',
]

@bot.command(name='zalgo')
async def zalgo_cmd(ctx, intensity='m', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}zalgo <l/m/h> <text>`')
    amount = {'l': 1, 'm': 3, 'h': 6}.get(intensity, 3)
    result = ''
    for c in text:
        result += c + ''.join(random.choice(ZALGO_CHARS[j % 3])
                    for j in range(amount))
    await ctx.send(result[:1900])


TINY_MAP = str.maketrans(
    'abcdefghijklmnopqrstuvwxyz0123456789',
    'ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖqʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹')

@bot.command(name='tinytext')
async def tinytext_cmd(ctx, *, text=''):
    if text:
        await ctx.send(text.lower().translate(TINY_MAP))


BUBBLE_MAP = str.maketrans(
    'abcdefghijklmnopqrstuvwxyz0123456789',
    '\u24D0\u24D1\u24D2\u24D3\u24D4\u24D5\u24D6\u24D7\u24D8'
    '\u24D9\u24DA\u24DB\u24DC\u24DD\u24DE\u24DF\u24E0\u24E1'
    '\u24E2\u24E3\u24E4\u24E5\u24E6\u24E7\u24E8\u24E9'
    '\u24EA\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468')

@bot.command(name='bubbletext')
async def bubbletext_cmd(ctx, *, text=''):
    if text:
        await ctx.send(text.lower().translate(BUBBLE_MAP))


SQUARE_MAP = str.maketrans(
    'abcdefghijklmnopqrstuvwxyz0123456789',
    ''.join(chr(0x1F130 + i) for i in range(26)) + '0123456789')

@bot.command(name='squaretext')
async def squaretext_cmd(ctx, *, text=''):
    if text:
        result = text.lower().translate(SQUARE_MAP)
        await ctx.send(result[:1900])


FANCY_FONTS = {
    'bold': str.maketrans('abcdefghijklmnopqrstuvwxyz',
        '\U0001D41A\U0001D41B\U0001D41C\U0001D41D\U0001D41E'
        '\U0001D41F\U0001D420\U0001D421\U0001D422\U0001D423'
        '\U0001D424\U0001D425\U0001D426\U0001D427\U0001D428'
        '\U0001D429\U0001D42A\U0001D42B\U0001D42C\U0001D42D'
        '\U0001D42E\U0001D42F\U0001D430\U0001D431\U0001D432\U0001D433'),
    'italic': str.maketrans('abcdefghijklmnopqrstuvwxyz',
        '\U0001D44E\U0001D44F\U0001D450\U0001D451\U0001D452'
        '\U0001D453\U0001D454\U0001D455\U0001D456\U0001D457'
        '\U0001D458\U0001D459\U0001D45A\U0001D45B\U0001D45C'
        '\U0001D45D\U0001D45E\U0001D45F\U0001D460\U0001D461'
        '\U0001D462\U0001D463\U0001D464\U0001D465\U0001D466\U0001D467'),
}

@bot.command(name='fancytext')
async def fancytext_cmd(ctx, font='bold', *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}fancytext bold/italic <text>`')
    table = FANCY_FONTS.get(font, FANCY_FONTS['bold'])
    await ctx.send(text.lower().translate(table))


@bot.command(name='strikethrough')
async def strikethrough_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'~~{text}~~')


@bot.command(name='header')
async def header_cmd(ctx, *, text=''):
    if text:
        await ctx.send(f'# {text}')


@bot.command(name='bullet')
async def bullet_cmd(ctx, *, text=''):
    if text:
        items = [i.strip() for i in text.split('|')]
        await ctx.send('\n'.join(f'- {i}' for i in items))


@bot.command(name='numbered')
async def numbered_cmd(ctx, *, text=''):
    if text:
        items = [i.strip() for i in text.split('|')]
        await ctx.send('\n'.join(f'{j}. {i}'
                    for j, i in enumerate(items, 1)))


@bot.command(name='checkbox')
async def checkbox_cmd(ctx, *, text=''):
    if not text:
        return
    items = [i.strip() for i in text.split('|')]
    checked = '\u2705'
    unchecked = '\u2B1C'
    result = '\n'.join(
        checked + ' ' + i.replace('[x] ', '').replace('[ ] ', '')
        if i.startswith('[x]')
        else unchecked + ' ' + i.replace('[x] ', '').replace('[ ] ', '')
        for i in items)
    await ctx.send(result)


# ============================================================
#  ANIMATED TEXT
# ============================================================
@bot.command(name='typewriter')
async def typewriter_cmd(ctx, speed: float = 1.0, *, text=''):
    if not text:
        return await ctx.send(f'Usage: `{PREFIX}typewriter <speed> <text>`')
    msg = await ctx.send(text[0])
    for i in range(2, len(text) + 1, 2):
        try:
            await msg.edit(content=text[:i])
        except Exception:
            break
        await asyncio.sleep(max(speed * 0.5, 0.3))


@bot.command(name='flash')
async def flash_cmd(ctx, *, text=''):
    if not text:
        return
    msg = await ctx.send(f'```{text}```')
    for style in [f'`{text}`', f'**{text}**', f'__{text}__',
                  f'~~{text}~~', text]:
        try:
            await msg.edit(content=style)
            await asyncio.sleep(0.7)
        except Exception:
            break
    await msg.edit(content=text)


@bot.command(name='wavetext')
async def wavetext_cmd(ctx, *, text=''):
    if not text:
        return
    result = ''
    up = True
    for i, c in enumerate(text):
        result += c.upper() if up else c.lower()
        if i % 2:
            up = not up
    await ctx.send(result)


@bot.command(name='rainbowtext')
async def rainbowtext_cmd(ctx, *, text=''):
    if not text:
        return
    # use quote blocks for pseudo-rainbow
    colors = ['', '`', '```', '__', '**']
    result = ''
    for i, c in enumerate(text):
        style = colors[i % len(colors)]
        result += f'{style}{c}{style}' if c != ' ' else ' '
    await ctx.send(result[:1900])


# ============================================================
#  STATS & ANALYTICS
# ============================================================
@bot.command(name='messagecount')
async def messagecount_cmd(ctx, user: discord.User = None, limit=500):
    user = user or ctx.author
    count = 0
    async for msg in ctx.channel.history(limit=min(limit, 1000)):
        if msg.author.id == user.id:
            count += 1
    await ctx.send(f'**{user}**: {count} messages '
                  f'in last {limit}')


@bot.command(name='wordcount')
async def wordcount_cmd(ctx, limit=200):
    words = 0
    msgs = 0
    async for msg in ctx.channel.history(limit=min(limit, 500)):
        if msg.author.id == bot.user.id:
            words += len(msg.content.split())
            msgs += 1
    await ctx.send(f'Your last {msgs} messages: **{words}** words '
                  f'({words // max(msgs, 1)} avg)')


@bot.command(name='serverstats')
async def serverstats_cmd(ctx):
    if not ctx.guild:
        return
    g = ctx.guild
    humans = sum(1 for m in g.members if not m.bot)
    bots = sum(1 for m in g.members if m.bot)
    online = sum(1 for m in g.members
                if str(m.status) != 'offline')
    e = bx_embed(f'Stats: {g.name}')
    e.add_field(name='Total', value=g.member_count)
    e.add_field(name='Humans', value=humans)
    e.add_field(name='Bots', value=bots)
    e.add_field(name='Online', value=online)
    e.add_field(name='Channels', value=len(g.channels))
    e.add_field(name='Roles', value=len(g.roles))
    await ctx.send(embed=e)


@bot.command(name='leaderboard')
async def leaderboard_cmd(ctx, limit=1000):
    if not ctx.guild:
        return
    counts = {}
    async for msg in ctx.channel.history(limit=min(limit, 2000)):
        uid = msg.author.id
        counts[uid] = counts.get(uid, 0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:10]
    lines = []
    for i, (uid, count) in enumerate(top, 1):
        member = ctx.guild.get_member(uid)
        name = member.name if member else f'<@{uid}>'
        lines.append(f'**{i}.** {name}: {count}')
    if lines:
        await ctx.send('\n'.join(lines))


@bot.command(name='oldestfriend')
async def oldestfriend_cmd(ctx):
    friends = sorted(bot.friends, key=lambda f: f.created_at)
    if friends:
        f = friends[0]
        await ctx.send(f'**{f}** (since {f.created_at.strftime("%Y-%m-%d")})')


@bot.command(name='newestfriend')
async def newestfriend_cmd(ctx):
    friends = sorted(bot.friends, key=lambda f: f.created_at,
                     reverse=True)
    if friends:
        f = friends[0]
        await ctx.send(f'**{f}** (since {f.created_at.strftime("%Y-%m-%d")})')


@bot.command(name='mutualservers')
async def mutualservers_cmd(ctx, user: discord.User):
    if user.id == bot.user.id:
        return await ctx.send('Use your own eyes.')
    mutual = [g.name for g in bot.guilds if g.get_member(user.id)][:15]
    if mutual:
        await ctx.send(f'**Mutual servers with {user}**\n'
                      + '\n'.join(f'- {g}' for g in mutual))
    else:
        await ctx.send('No mutual servers.')


@bot.command(name='mutualfriends')
async def mutualfriends_cmd(ctx, user: discord.User):
    my_friends = {f.id for f in bot.friends}
    their_friends = set()
    try:
        for rel in await bot.http.get_mutual_friends(user.id):
            if rel.get('type') == 1:
                their_friends.add(rel.get('user_id'))
    except Exception:
        pass
    mutual = my_friends & their_friends
    if mutual:
        names = []
        for fid in list(mutual)[:10]:
            friend = bot.get_user(fid)
            if friend:
                names.append(f'`{friend.name}`')
        await ctx.send(f'**Mutual friends:** ' + ' '.join(names))
    else:
        await ctx.send('No mutual friends found.')


@bot.command(name='discriminator')
async def discriminator_cmd(ctx):
    u = bot.user
    if hasattr(u, 'discriminator') and u.discriminator != '0':
        await ctx.send(f'Your discrim: `#{u.discriminator}`')
    else:
        await ctx.send('New username system (no discrim).')


# ============================================================
#  TAGS (custom shortcuts)
# ============================================================
TAGS_FILE = DATA_DIR / 'tags.json'
TAGS = _load('tags.json')

@bot.command(name='tag')
async def tag_cmd(ctx, name='', *, content=''):
    if not name:
        return await ctx.send(f'Usage: `{PREFIX}tag <name> [content]`')
    if content:
        TAGS[name.lower()] = content
        _save('tags.json', TAGS)
        await ctx.send(f'Tag `{name}` saved.')
    elif name.lower() in TAGS:
        await ctx.send(TAGS[name.lower()])
    else:
        await ctx.send(f'Tag `{name}` not found.')


@bot.command(name='mytags')
async def mytags_cmd(ctx):
    if TAGS:
        await ctx.send(', '.join(f'`{k}`' for k in TAGS))
    else:
        await ctx.send('No tags saved.')


@bot.command(name='tagdel')
async def tagdel_cmd(ctx, name=''):
    if name.lower() in TAGS:
        TAGS.pop(name.lower())
        _save('tags.json', TAGS)
        await ctx.send(f'Deleted `{name}`.')
    else:
        await ctx.send(f'`{name}` not found.')


# ============================================================
#  SCHEDULING
# ============================================================
SCHEDULES_FILE = DATA_DIR / 'schedules.json'
SCHEDULES = _load('schedules.json')

@bot.command(name='schedule')
async def schedule_cmd(ctx, delay_minutes: float = 0, *, message=''):
    if delay_minutes <= 0 or not message:
        return await ctx.send(
            f'Usage: `{PREFIX}schedule <minutes> <message>`')
    import uuid as _uuid
    sid = str(_uuid.uuid4())[:8]
    SCHEDULES[sid] = {
        'time': time.time() + delay_minutes * 60,
        'message': message,
        'channel': ctx.channel.id,
    }
    _save('schedules.json', SCHEDULES)
    await ctx.send(f'Scheduled in {delay_minutes}m (id: `{sid}`)')
    async def _send_later():
        await asyncio.sleep(delay_minutes * 60)
        ch = bot.get_channel(ctx.channel.id)
        if ch:
            try:
                await ch.send(message)
            except Exception:
                pass
    bot.loop.create_task(_send_later())


@bot.command(name='cancelschedule')
async def cancelschedule_cmd(ctx, sid=''):
    if sid in SCHEDULES:
        SCHEDULES.pop(sid)
        _save('schedules.json', SCHEDULES)
        await ctx.send(f'Cancelled `{sid}`.')
    else:
        await ctx.send(f'`{sid}` not found.')


@bot.command(name='countdown')
async def countdown_cmd(ctx, seconds: int = 10):
    seconds = min(seconds, 60)
    msg = await ctx.send(f':timer: **{seconds}**')
    while seconds > 0:
        await asyncio.sleep(1)
        seconds -= 1
        try:
            await msg.edit(content=f':timer: **{seconds}**')
        except Exception:
            return
    try:
        await msg.edit(content=':tada: **Done!**')
    except Exception:
        pass


@bot.command(name='stopwatch')
async def stopwatch_cmd(ctx):
    start = time.perf_counter()
    msg = await ctx.send(':stopwatch: **0.0s**')
    for _ in range(30):
        await asyncio.sleep(1)
        elapsed = time.perf_counter() - start
        try:
            await msg.edit(
                content=f':stopwatch: **{elapsed:.1f}s**')
        except Exception:
            return
    await ctx.send(f'Final: **{time.perf_counter() - start:.1f}s**')


# ============================================================
#  MODES
# ============================================================
GHOST_MODE = False

@bot.command(name='ghostmode')
async def ghostmode_cmd(ctx):
    global GHOST_MODE
    GHOST_MODE = not GHOST_MODE
    state = 'ON (messages auto-delete after 5s)' if GHOST_MODE else 'OFF'
    await ctx.send(f'Ghost mode: **{state}**')


@bot.command(name='stealthmode')
async def stealthmode_cmd(ctx):
    await bot.change_presence(status=discord.Status.invisible)
    await ctx.send('Invisible + no activity set. '
                  'You are now a shadow.')


@bot.command(name='setbanner')
async def setbanner_cmd(ctx, url=''):
    if not url:
        return await ctx.send(f'Usage: `{PREFIX}setbanner <url>`')
    if requests:
        try:
            img = requests.get(url, timeout=10).content
            await bot.user.edit(banner=img)
            await ctx.send('Banner updated.')
        except Exception as e:
            await ctx.send(f'`{e}`')


@bot.command(name='notificationsound')
async def notificationsound_cmd(ctx, state=''):
    if state.lower() == 'on':
        CONFIG['notif_sound'] = True
        _save('config.json', CONFIG)
        await ctx.send('Notification sound: ON (plays on nitro snipe)')
    else:
        CONFIG['notif_sound'] = False
        _save('config.json', CONFIG)
        await ctx.send('Notification sound: OFF')


# ============================================================
#  DISCORD INTERNALS
# ============================================================
@bot.command(name='auditlog')
async def auditlog_cmd(ctx, limit=5):
    if not ctx.guild:
        return
    try:
        entries = [e async for e in
                   ctx.guild.audit_logs(limit=min(limit, 10))]
        if entries:
            lines = []
            for entry in entries:
                action = str(entry.action).split('.')[-1]
                target = getattr(entry.target, 'name',
                                str(entry.target))
                lines.append(
                    f'**{entry.user}** -> {action} -> '
                    f'{target} ({entry.created_at.strftime("%H:%M")})')
            await ctx.send('\n'.join(lines))
        else:
            await ctx.send('No audit log entries.')
    except discord.Forbidden:
        await ctx.send('No permission to view audit log.')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='modlog')
async def modlog_cmd(ctx, limit=10):
    await auditlog_cmd(ctx, limit)


@bot.command(name='afklist')
async def afklist_cmd(ctx):
    afk_users = []
    if ctx.guild:
        for m in ctx.guild.members:
            if hasattr(m, 'status') and str(m.status) == 'idle':
                afk_users.append(f'`{m.name}`')
    if afk_users:
        await ctx.send(f'Idle users: ' + ' '.join(afk_users[:15]))
    else:
        await ctx.send('No idle users found.')


# ============================================================
#  MASS ACTIONS (careful with these)
# ============================================================
@bot.command(name='massnick')
async def massnick_cmd(ctx, *, nickname=''):
    if not ctx.guild:
        return
    changed = 0
    for member in ctx.guild.members[:20]:
        try:
            await member.edit(nick=nickname or None)
            changed += 1
            await asyncio.sleep(0.5)
        except Exception:
            pass
    await ctx.send(f'Changed {changed} nicknames.')


@bot.command(name='massrole')
async def massrole_cmd(ctx, *, role_name=''):
    if not role_name or not ctx.guild:
        return
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send('Role not found.')
    given = 0
    for member in ctx.guild.members[:20]:
        if role not in member.roles:
            try:
                await member.add_roles(role)
                given += 1
                await asyncio.sleep(0.5)
            except Exception:
                pass
    await ctx.send(f'Gave role to {given} members.')


# ============================================================
#  EXTRA LOOKUP
# ============================================================
@bot.command(name='chart')
async def chart_cmd(ctx, coin='bitcoin', days=7):
    if not requests:
        return
    try:
        await ctx.send(
            f'https://charts.coingecko.com/coins/{coin}/'
            f'usd/{days}d/chart.png')
    except Exception:
        await ctx.send('Failed.')


@bot.command(name='nft')
async def nft_cmd(ctx, *, collection=''):
    if not collection or not requests:
        return await ctx.send(f'Usage: `{PREFIX}nft <collection>`')
    try:
        r = requests.get(
            f'https://api.opensea.io/api/v2/collections/'
            f'{collection}/stats', timeout=10)
        if r.status_code == 200:
            d = r.json()
            await ctx.send(
                f'**{collection}**\n'
                f'Floor: `{d.get("stats", {}).get("floor_price", "?")} ETH` | '
                f'Volume: `{d.get("stats", {}).get("total_volume", "?")} ETH`')
        else:
            await ctx.send('Collection not found.')
    except Exception:
        await ctx.send('Failed.')


@bot.command(name='avatarhistory')
async def avatarhistory_cmd(ctx, user: discord.User = None):
    user = user or ctx.author
    try:
        avatars = await user.avatar_url_as(format=None).read()
    except Exception:
        pass
    if user.avatar:
        await ctx.send(f'Most recent: {user.avatar.url}\n'
                      '(full history requires cached data)')
    else:
        await ctx.send('No avatar set.')


# ============================================================
#  AUTO-RESPOND CONFIG
# ============================================================
@bot.command(name='autorespond')
async def autorespond_cmd(ctx, trigger='', *, response=''):
    if not trigger or not response:
        if KEYWORD_RESPONSES:
            lines = [f'`{k}` -> `{v[:40]}`'
                    for k, v in KEYWORD_RESPONSES.items()]
            await ctx.send('\n'.join(lines))
        else:
            await ctx.send(
                f'Usage: `{PREFIX}autorespond <trigger> <response>`')


@bot.command(name='triggerlist')
async def triggerlist_cmd(ctx):
    if KEYWORD_RESPONSES:
        await ctx.send('\n'.join(
            f'`{k}` -> `{v[:40]}`'
            for k, v in KEYWORD_RESPONSES.items()))
    else:
        await ctx.send('No triggers set.')


@bot.command(name='triggerdel')
async def triggerdel_cmd(ctx, *, trigger=''):
    if trigger.lower() in KEYWORD_RESPONSES:
        KEYWORD_RESPONSES.pop(trigger.lower())
        await ctx.send(f'Removed trigger `{trigger}`.')
    else:
        await ctx.send(f'Trigger `{trigger}` not found.')


# ============================================================
#  SERVER MANAGEMENT
# ============================================================
@bot.command(name='roleinfo')
async def roleinfo_cmd(ctx, *, role_name=''):
    if not role_name or not ctx.guild:
        return await ctx.send(f'Usage: `{PREFIX}roleinfo <name>`')
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send('Role not found.')
    e = bx_embed(f'Role: {role.name}', color=role.color.value)
    e.add_field(name='ID', value=role.id)
    e.add_field(name='Members', value=len(role.members))
    e.add_field(name='Position', value=role.position)
    e.add_field(name='Color', value=str(role.color))
    e.add_field(name='Hoisted', value=str(role.hoist))
    e.add_field(name='Mentionable', value=str(role.mentionable))
    await ctx.send(embed=e)


@bot.command(name='boosters')
async def boosters_cmd(ctx):
    if not ctx.guild:
        return
    boosters = [m for m in ctx.guild.members
                if m.premium_since]
    if not boosters:
        return await ctx.send('No boosters.')
    e = bx_embed(f'Boosters ({len(boosters)})')
    for m in boosters[:20]:
        since = m.premium_since.strftime('%Y-%m-%d')
        e.add_field(name=str(m), value=since, inline=True)
    await ctx.send(embed=e)


@bot.command(name='serveremojis')
async def serveremojis_cmd(ctx):
    if not ctx.guild:
        return
    emojis = ctx.guild.emojis
    if not emojis:
        return await ctx.send('No custom emojis.')
    regular = [f'<:{e.name}:{e.id}>' for e in emojis
               if not e.animated][:30]
    animated = [f'<a:{e.name}:{e.id}>' for e in emojis
                if e.animated][:30]
    text = ' '.join(regular + animated)
    if text:
        await ctx.send(text)
    else:
        await ctx.send('Too many emojis to display.')


@bot.command(name='stealemoji')
async def stealemoji_cmd(ctx, emoji=''):
    if not emoji:
        return await ctx.send(f'Usage: `{PREFIX}stealemoji :emoji:`')
    m = re.search(r'<a?:(\w+):(\d+)>', emoji)
    if not m:
        return await ctx.send('Invalid format.')
    name, eid = m.groups()
    ext = 'gif' if emoji.startswith('<a:') else 'png'
    url = f'https://cdn.discordapp.com/emojis/{eid}.{ext}'
    for guild in bot.guilds:
        if guild.me and \
                guild.me.guild_permissions.manage_emojis:
            try:
                if requests:
                    img = requests.get(url).content
                    await guild.create_custom_emoji(
                        name=name, image=img)
                    return await ctx.send(
                        f'Stole to **{guild.name}**')
            except Exception:
                continue
    await ctx.send('No server with emoji perms.')


@bot.command(name='nick')
async def nick_cmd(ctx, *, nickname=''):
    if not ctx.guild:
        return
    try:
        await ctx.guild.me.edit(nick=nickname or None)
        await ctx.send(f'Nick: **{nickname or "reset"}**')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='setname')
async def setname_cmd(ctx, *, name=''):
    if not name:
        return await ctx.send(f'Usage: `{PREFIX}setname <name>`')
    try:
        await bot.user.edit(username=name)
        await ctx.send(f'Username: **{name}**')
    except Exception as e:
        await ctx.send(f'`{e}`')


@bot.command(name='slowmode')
async def slowmode_cmd(ctx, seconds: int = 0):
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f'Slowmode: **{seconds}s**')
    except Exception as e:
        await ctx.send(f'`{e}`')


# ============================================================
#  BACKUP
# ============================================================
@bot.command(name='backupfriends')
async def backupfriends_cmd(ctx):
    friends = [{'user': str(f), 'id': f.id}
               for f in bot.friends]
    _save('friends_backup.json', friends)
    await ctx.send(f'Backed up {len(friends)} friends')


@bot.command(name='backupservers')
async def backupservers_cmd(ctx):
    servers = [{'name': g.name, 'id': g.id}
               for g in bot.guilds]
    _save('servers_backup.json', servers)
    await ctx.send(f'Backed up {len(servers)} servers')


@bot.command(name='backupemojis')
async def backupemojis_cmd(ctx):
    if not ctx.guild:
        return
    emojis = [{'name': e.name,
               'id': e.id,
               'animated': e.animated}
              for e in ctx.guild.emojis]
    _save('emoji_backup.json', emojis)
    await ctx.send(f'Backed up {len(emojis)} emojis')


@bot.command(name='firstmessage')
async def firstmessage_cmd(ctx,
                           channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    async for msg in channel.history(limit=1, oldest_first=True):
        await ctx.send(f'{msg.jump_url}')
        return
    await ctx.send('No messages.')


@bot.command(name='copyembed')
async def copyembed_cmd(ctx):
    async for msg in ctx.channel.history(limit=20):
        if msg.embeds:
            data = msg.embeds[0].to_dict()
            await ctx.send(
                f'```json\n{json.dumps(data, indent=2)}\n```')
            return
    await ctx.send('No embeds found.')


# ============================================================
#  EVENTS (nitro, giveaway, AFK, auto-react, snipe, keywords)
# ============================================================
@bot.event
async def on_message(message):
    global SNIPE_COUNT, GIVEAWAY_COUNT
    if message.author.id == bot.user.id:
        if message.content.startswith(PREFIX):
            log.info(f'Command triggered: {message.content}')
        await bot.process_commands(message)
        return

    # Nitro sniper
    for code in re.findall(
            r'(?:discord\.gift/|discord\.com/gifts/)'
            r'([A-Za-z0-9]{16,25})', message.content):
        SNIPE_COUNT += 1
        log.info(f'Nitro: {code}')
        try:
            await bot.http.post(
                '/entitlements/gift-codes/' + code + '/redeem')
            if NITRO_WEBHOOK and requests:
                requests.post(NITRO_WEBHOOK, json={
                    'content': f'**Nitro sniped!** `{code}`'})
        except Exception as e:
            log.warning(f'Nitro failed: {e}')

    # Giveaway joiner
    if message.guild and \
            'giveaway' in message.content.lower():
        for reaction in message.reactions:
            if str(reaction.emoji) in ('\U0001F389',
                                       '\U0001F38A',
                                       '\U0001F381'):
                try:
                    await message.add_reaction(reaction.emoji)
                    GIVEAWAY_COUNT += 1
                except Exception:
                    pass
                break

    # Auto-react
    if AUTO_REACT_ENABLED and AUTO_REACT_EMOJI and \
            message.guild:
        try:
            await message.add_reaction(AUTO_REACT_EMOJI)
        except Exception:
            pass

    # AFK responder
    if AFK and bot.user.mentioned_in(message):
        try:
            await message.reply(AFK_MESSAGE,
                               mention_author=False)
        except Exception:
            pass

    # Keyword responder
    lower = message.content.lower()
    for kw, resp in KEYWORD_RESPONSES.items():
        if kw in lower:
            try:
                await message.reply(resp,
                                   mention_author=False)
            except Exception:
                pass
            break


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    log.error(f'Command error in {ctx.command}: {error}', exc_info=error)
    try:
        await ctx.send(f':x: Error: `{error}`')
    except Exception:
        pass


@bot.event
async def on_message_delete(message):
    SNIPED_MESSAGES[message.channel.id] = {
        'content': message.content,
        'author': str(message.author),
        'attachments': message.attachments[0].url
        if message.attachments else None}


@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        EDIT_SNIPED[before.channel.id] = {
            'before': before.content[:1000],
            'after': after.content[:1000]}


# ============================================================
#  MAIN
# ============================================================
if __name__ == '__main__':
    if not TOKEN or TOKEN == "PASTE_YOUR_DISCORD_TOKEN_HERE":
        print(r"""
    +==========================================+
    |                                          |
    |   Byte X Selfbot - Full Nighty Commands  |
    |                                          |
    |   Recovered from PyArmor by Byte X       |
    |   https://gang.baby/                     |
    |                                          |
    |   226 commands | Nitro sniper            |
    |   Spotify | RPC | AFK | Auto-react       |
    |   Giveaway joiner | Message sniping      |
    |                                          |
    |   Paste your Discord token below to run. |
    |   (Saved securely to your local config)  |
    |                                          |
    |   Use .help for all commands             |
    |                                          |
    +==========================================+
        """)
        try:
            entered = input("  Paste Discord token: ").strip().strip('"').strip("'")
            if entered:
                TOKEN = entered
                CONFIG['token'] = TOKEN
                _save('config.json', CONFIG)
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)

    if TOKEN and TOKEN != "PASTE_YOUR_DISCORD_TOKEN_HERE":
        bot.run(TOKEN)
    else:
        print("No token provided. Exiting.")
