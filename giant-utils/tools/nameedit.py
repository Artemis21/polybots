"""Utility to allow people to rename channels."""
import re

import discord

from .roles import mass_un_role


LANGUAGE = [
    'po', 'ly', 'lu', 'mi', 'lo', 'da', 'bi', 'oo', 'sa', 'ko', 'me', 'da',
    'to', 'pi', 'as', 'an', 'ki'
]
ACTIONS = [
    'Clowns', 'Bongo', 'Duh!', 'Squeal', 'Squirrel', 'Confusion', 'Gruff',
    'Moan', 'Chickens', 'Spunge', 'Gnomes', 'Bell-boys', 'Gurkins',
    'Commotion', 'LOL', 'Shenanigans', 'Hullabaloo', 'Papercuts', 'Eggs',
    'Mooni', 'Gaami', 'War', 'Spirit', 'Faith', 'Glory', 'Blood', 'Empires',
    'Songs', 'Dawn', 'Prophecy', 'Gold', 'Fire', 'Swords', 'Queens',
    'Knights', 'Kings', 'Tribes', 'Tales', 'Quests', 'Change', 'Games',
    'Throne', 'Conquest', 'Struggle', 'Victory', 'Battles', 'Legends',
    'Heroes', 'Storms', 'Clouds', 'Gods', 'Love', 'Lords', 'Lights', 'Wrath',
    'Destruction', 'Whales', 'Ruins', 'Monuments', 'Wonder'
]
SUPERLATIVES = [
    'Epic', 'Endless', 'Glorious', 'Brave', 'Misty', 'Mysterious', 'Lost',
    'Cold', 'Amazing', 'Doomed', 'Glowing', 'Glimmering', 'Magical', 'Living',
    'Thriving', 'Bold', 'Dark', 'Bright', 'Majestic', 'Shimmering', 'Lucky',
    'Great', 'Everlasting', 'Eternal', 'Superb', 'Frozen', 'Gruffy', 'Slimy',
    'Silly', 'Unwilling', 'Stumbling', 'Drunken', 'Merry', 'Mediocre',
    'Normal', 'Stupid', 'Moody', 'Tipsy', 'Trifling', 'Rancid', 'Numb'
]
NATURES = [
    'Hills', 'Fields', 'Lands', 'Forest', 'Ocean', 'Fruit', 'Mountain', 'Lake',
    'Paradise', 'Jungle', 'Desert', 'River', 'Sea', 'Shores', 'Valley',
    'Garden', 'Moon', 'Star', 'Winter', 'Spring', 'Summer', 'Autumn',
    'Divide', 'Square', 'Glacier', 'Ice', 'Custard', 'Goon', 'Cat',
    'Spagetti', 'Fish', 'Fame', 'Popcorn', 'Dessert', 'Space'
]


def _is_renameable(channel: discord.TextChannel) -> bool:
    """Check if a channel may be renamed."""
    if not channel.category:
        return False
    return len(channel.category.name) == 2


def _place_is_valid(place: str) -> bool:
    """Check if the place part of a game name is real."""
    first = '|'.join(syllable.title() for syllable in LANGUAGE)
    later = '|'.join(LANGUAGE)
    regex = f'({first})({later}){{1,2}}$'
    return re.match(regex, place)


def _name_is_valid(name: str) -> bool:
    """Check if a game name is real."""
    # Bell boys is the only component with a space in, but we store it with a
    # dash instead since we use spaces to split up components.
    if 'Bell-boys' in name:
        return False
    name = name.replace('Bell boys', 'Bell-boys')
    parts = name.split()
    if parts[0] == 'The':
        if len(parts) == 3:
            return (parts[1] in SUPERLATIVES) and (parts[2] in NATURES)
        elif len(parts) == 4 and parts[2] == 'of':
            return (parts[1] in NATURES) and (parts[3] in ACTIONS)
    elif len(parts) == 2:
        if parts[0].endswith('ian'):
            if _place_is_valid(parts[0][:-3]):
                return (parts[1] in ACTIONS) or (parts[1] in NATURES)
            return False
        return (parts[0] in SUPERLATIVES) and (parts[1] in ACTIONS)
    elif len(parts) == 3:
        if parts[1] == '&':
            return (parts[0] in NATURES) and (parts[2] in ACTIONS)
        elif parts[1] == 'of':
            if _place_is_valid(parts[2]):
                return (parts[0] in ACTIONS) or (parts[0] in NATURES)
    return False


async def rename(channel: discord.TextChannel, new_name: str) -> str:
    """Rename a channel."""
    if not _is_renameable(channel):
        return 'This is not a game channel!'
    if not _name_is_valid(new_name):
        return (
            f'`{new_name}` is not a valid game name. Make sure to type it'
            ' exactly as it appears in-game.'
        )
    await channel.edit(name=new_name)
    return 'Channel renamed :thumbsup:'


async def reset(
        channel: discord.TextChannel, any_channel: bool = False,
        topic: str = '') -> str:
    """Reset all channels in a category."""
    if not (any_channel or _is_renameable(channel)):
        return 'This is not a division category!'
    overwrites = channel.overwrites
    category = channel.category
    for channel in category.channels:
        await channel.delete()
    new_names = [
        'time-out-glitches-and-breaks', 'general',
        *['game-' + str(i) for i in range(1, 9)]
    ]
    for name in new_names:
        await category.create_text_channel(
            name, overwrites=overwrites, topic=topic
        )


async def reset_guild(guild: discord.Guild) -> str:
    """Reset all division categories, and some other channels/roles."""
    cat_count = 0
    role_count = 0
    # In case guild.categories changes during iteration.
    categories = list(guild.categories)
    for cat in categories:
        if cat.text_channels:
            # reset will return error if not division cat, no need to check.
            error = await reset(
                cat.text_channels[0],
                topic='https://www.youtube.com/watch?v=oHg5SJYRHA0'
            )
            if not error:
                role = discord.utils.get(guild.roles, name=f'Division {cat}')
                if role:
                    await mass_un_role(role)
                    role_count += 1
                cat_count += 1
    follow_up_cat = guild.get_channel(749979803150712965)
    await reset(follow_up_cat, any_channel=True)
    extra_roles = [685862261150973994, 754208236734906379, 751867341809254402]
    for role_id in extra_roles:
        role = guild.get_role(role_id)
        await mass_un_role(role)
    return (
        f'Reset {cat_count} division categories, {role_count} division '
        f'roles, the FOLLOW-UP category and {len(extra_roles)} extra roles.'
    )
