"""Tool to archive finalists channels."""
import aiohttp
import base64
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
        print(json.dumps(data, indent=4))
        return data['data']['link']


async def download_image(attachment: discord.Attachment) -> str:
    """Download an image from Discord and convert to b64."""
    data = await attachment.read()
    data = base64.b64encode(data)
    typ = attachment.filename.split('.')[-1]
    return f'data:image/{typ};base64{data.decode()}'


async def archive_channel(
        channel: discord.TextChannel, member: discord.Member) -> str:
    """Archive messages from a user in a text channel."""
    pieces = []
    async for message in channel.history(limit=None, oldest_first=True):
        if message.author.id == member.id:
            if message.content:
                pieces.append({'type': 'text', 'value': message.content})
            for attachment in message.attachments:
                # url = await imgur_upload(attachment.url)
                # Imgur ratelimits are too high, so download instead
                url = await download_image(attachment)
                pieces.append({'type': 'image', 'value': url})
    title = channel.name.replace('-', ' ').title()
    return pastebin.upload(TEMPLATE.render(pieces=pieces, title=title))


async def archive_channels(search: str):
    """Archive a set of channels by search."""
    lines = []
    for channel in CONFIG.guild.text_channels:
        if search in channel.name:
            print(channel.name)
            member = discord.utils.find(
                lambda u: u.name.lower() in channel.name.split('-'),
                CONFIG.guild.members
            )
            print(f'{channel} / {member}')
            link = await archive_channel(channel, member)
            lines.append(f'{channel.mention}: {link}')
    return '\n'.join(lines)
