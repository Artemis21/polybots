"""Tool to archive finalists channels."""
import aiohttp
import json

import discord

import jinja2


from tools import config, pastebin


CONFIG = config.Config()

env = jinja2.Environment(autoescape=jinja2.select_autoescape())
TEMPLATE = env.from_string('''
{{ title }}
{%- for piece in pieces -%}
    {%- if piece.type == 'text' -%}
        <p>{{ piece.value }}</p>
    {%- elif piece.type == 'image' -%}
        <img src="{{ piece.value }}"/>
    {%- else -%}
        WARNING: Unrecognised piece type "{{ piece.type }}"!
        Value: "{{ piece.value }}".
    {%- endif -%}
{%- endfor -%}
''')

IMGUR_API = 'https://api.imgur.com/3/'
with open('config.json') as f:
    IMGUR_ID = json.load(f)['imgur_id']

SESSION = aiohttp.ClientSession()


async def imgur_upload(url: str) -> str:
    """Upload an image to imgur from a URL."""
    async with SESSION.post(
            url=IMGUR_API + 'image',
            headers={'Authorization': 'Client-ID ' + IMGUR_ID},
            data={'image': url, 'type': 'url'}
            ) as resp:
        data = await resp.json()
        return data['data']['link']


async def archive_channel(
        channel: discord.TextChannel, member: discord.Member) -> str:
    """Archive messages from a user in a text channel."""
    pieces = []
    async for message in channel.history(limit=None, oldest_first=True):
        if message.author.id == member.id:
            if message.content:
                pieces.append({'type': 'text', 'value': message.content})
            for attachment in message.attachments:
                url = await imgur_upload(attachment.url)
                pieces.append({'type': 'image', 'value': url})
    title = channel.name.replace('-', ' ').title()
    return pastebin.upload(TEMPLATE.render(pieces=pieces, title=title))


async def archive_channels(search: str):
    """Archive a set of channels by search."""
    lines = []
    for channel in CONFIG.guild.text_channels:
        if search in channel.name:
            member = discord.utils.find(
                lambda u: u.name.lower() in channel.name.split('-'),
                CONFIG.guild.members
            )
            link = await archive_channel(channel, member))
            lines.append(f'{channel.mention}: {link}')
    return '\n'.join(lines)
