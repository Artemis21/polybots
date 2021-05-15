"""Read JSON config for the bot."""
import json
import logging
import pathlib
from datetime import timedelta


BASE_PATH = pathlib.Path(__file__).parent.parent.parent

with open(str(BASE_PATH / 'config.json')) as f:
    config = json.load(f)


def get_colour(field: str, default: int) -> int:
    """Parse a colour from the config file."""
    raw = config.get(field)
    if not raw:
        return default
    if isinstance(raw, int):
        return raw
    return int(raw[1:], 16)


def get_log_level(field: str, default: int) -> int:
    """Parse a logging level field from the config file."""
    raw = config.get(field)
    if not raw:
        return default
    return {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'notset': logging.NOTSET,
        'none': logging.NOTSET
    }[raw.lower()]


def get_timedelta(field: str, default: timedelta) -> timedelta:
    """Parse a timedelta in config."""
    raw = config.get(field)
    if not raw:
        return default
    periods = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
        'w': 60 * 60 * 24 * 7,
        'M': 60 * 60 * 24 * 30,
        'y': 60 * 60 * 24 * 365
    }
    seconds = 0
    for part in raw.split():
        period_symbol = part[-1]
        value = int(part[:-1])
        seconds += value * periods[period_symbol]
    return timedelta(seconds=seconds)


BOT_PREFIX = config.get('bot_prefix', 't!')
BOT_TOKEN = config['bot_token']
BOT_ADMIN_ROLE_ID = config['bot_admin_role_id']
BOT_PLAYER_ROLE_ID = config['bot_player_role_id']
BOT_LOG_CHANNEL_ID = config.get('bot_log_channel_id', None)
BOT_GUILD_ID = config['bot_guild_id']
BOT_LOG_LEVEL = get_log_level('bot_log_level', logging.INFO)

ELO_BASE_URL = config.get('elo_base_url', 'https://elo-bot.polytopia.win')
ELO_USERNAME = config['elo_username']
ELO_PASSWORD = config['elo_password']
ELO_RECHECK_TIME = get_timedelta('elo_recheck_time', timedelta(hours=25))
ELO_RECHECK_FREQUENCY = get_timedelta(
    'elo_recheck_frequency', timedelta(minutes=30)
)
ELO_GUILD_ID = config['elo_guild_id']

DB_NAME = config.get('db_name', 'ttt')
DB_USER = config.get('db_user', 'ttt')
DB_HOST = config.get('db_host', '127.0.0.1')
DB_PORT = config.get('db_port', 5432)
DB_PASSWORD = config['db_password']
DB_LOG_LEVEL = get_log_level('db_log_level', logging.INFO)

COL_ACCENT = get_colour('col_accent', 0xc64191)
COL_ERROR = get_colour('col_error', 0xe94b3c)
COL_HELP = get_colour('col_help', 0x50c878)

TT_LOG_LEVEL = get_log_level('tt_log_level', logging.INFO)
TT_GAME_TYPES = config.get('tt_game_types', [
    {
        'map': 'Dryland',
        'tribe': 'Yadakk',
        'alt_tribe': 'Oumaji'
    }, {
        'map': 'Lakes',
        'tribe': 'Luxidoor',
        'alt_tribe': 'Bardur'
    }, {
        'map': 'Continents',
        'tribe': 'Zebasi',
        'alt_tribe': 'Imperius'
    }, {
        'map': 'Archipelago',
        'tribe': 'Polaris',
        'alt_tribe': 'Imperius'
    }, {
        'map': 'Drylands',
        'tribe': 'Hoodrick',
        'alt_tribe': 'Bardur'
    }, {
        'map': 'Continents',
        'tribe': 'Cymanti',
        'alt_tribe': 'Bardur'
    }, {
        'map': 'Water World',
        'tribe': 'Vengir',
        'alt_tribe': 'Oumaji'
    }, {
        'map': 'Lakes',
        'tribe': 'Queztali',
        'alt_tribe': 'Xin-xi'
    }, {
        'map': 'Dryland',
        'tribe': 'Ai-Mo',
        'alt_tribe': 'Xin-xi'
    }, {
        'map': 'Lakes',
        'tribe': 'Elyrion',
        'alt_tribe': 'Imperius'
    }, {
        'map': 'Archipelago',
        'tribe': 'Aquarion',
        'alt_tribe': 'Oumaji'
    }, {
        'map': 'Continents',
        'tribe': 'Kickoo',
        'alt_tribe': 'Xin-xi'
    }
])
