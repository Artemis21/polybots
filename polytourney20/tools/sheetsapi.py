"""Tools for interacting with the spreadsheet."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import typing
from collections import namedtuple
from tools.cache import cache, DONT_CACHE
import string


SCOPE = [
    'https://spreadsheets.google.com/feeds', 
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

CREDS = ServiceAccountCredentials.from_json_keyfile_name('creds.json', SCOPE)
client = gspread.authorize(CREDS)
spread_sheet = client.open('ffatourney1')

Player = namedtuple(
    'Player',
    [
        'discord_name',
        'polytopia_name',
        'friend_code',
        'elo',
        'wins',
        'losses',
        'total_games',
        'games_in_progress',
        'needs_games',
        'host',
        'second',
        'third',
        'row'
    ]
)
StaticPlayer = namedtuple(
    'StaticPlayer',
    [
        'discord_name',
        'polytopia_name',
        'friend_code',
        'elo',
        'row'
    ]
)
Game = namedtuple(
    'Game',
    [
        'player1',
        'player2',
        'player3',
        'winner',
        'loser1',
        'loser2',
        'level',
        'id'
    ]
)


def get_game_id(level: int, row: int) -> str:
    if level == 0:
        level = 10
    num = int(f'{level}{row}')
    b36 = ''
    digits = string.digits + string.ascii_uppercase
    while num:
        b36 = digits[int(num % 36)] + b36
        num = int(num / 36)
    return b36


def get_game_row(gameid: str) -> typing.Tuple[int, int]:
    gameid = str(int(gameid, 36))
    if gameid[:2] == '10':
        level = 0
        row = int(gameid[2:])
    else:
        level = int(gameid[0])
        row = int(gameid[1:])
    return level, row


@cache
def get_sheet(
        name: typing.Optional[str] = None, *,
        level: typing.Optional[int] = None
        ) -> typing.Optional[gspread.Worksheet]:
    """Get a spreadsheet, using caching."""
    if level is not None:
        name = f'Level {level}'
    sheet = spread_sheet.worksheet(name)
    return sheet


@cache
def get_players_static() -> typing.List[StaticPlayer]:
    """Get a list of users, but only static attributes (for caching)."""
    sheet = get_sheet('Player Hub')
    records = sheet.get_all_records(head=6)
    players = []
    for row, record in enumerate(records):
        if not record['Discord Name:']:
            continue
        players.append(StaticPlayer(
            discord_name=record['Discord Name:'] or 'Not found',
            polytopia_name=record['Polytopia Name:'] or 'Not found',
            friend_code=record['Friend Code:'] or 'Not found',
            elo=record['ELO'] or 1000,
            row=row + 2
        ))
    return players


def get_players() -> typing.List[Player]:
    """Get a list of every user."""
    sheet = get_sheet('Player Hub')
    records = sheet.get_all_records(head=6)
    players = []
    for row, record in enumerate(records):
        if not record['Discord Name:']:
            continue
        players.append(Player(
            discord_name=record['Discord Name:'] or 'Not found',
            polytopia_name=record['Polytopia Name:'] or 'Not found',
            friend_code=record['Friend Code:'] or 'Not found',
            elo=record['ELO'] or 1000,
            wins=record['Wins:'] or 0,
            losses=record['Losses'] or 0,
            total_games=record['Total Games'] or 0,
            games_in_progress=record['Games in Progress'] or 0,
            needs_games=record['Needs Games'] != 'No',
            host=record['Host'] or 0,
            second=record['2nd'] or 0,
            third=record['3rd'] or 0,
            row=row + 2
        ))
    return players


def all_games(level: int) -> typing.List[Game]:
    """Find all games on a level."""
    sheet = get_sheet(level=level)
    raw_games = sheet.get_all_records()
    games = []
    for row, raw_game in enumerate(raw_games):
        if not raw_game['HOST']:
            continue
        if raw_game['WINNER'] == 'UNFINISHED':
            raw_game['WINNER'] = ''
        games.append(Game(
            player1=raw_game['HOST'],
            player2=raw_game['2nd PICK'],
            player3=raw_game['3rd PICK'],
            winner=raw_game['WINNER'],
            loser1=raw_game['LOSER 1'],
            loser2=raw_game['LOSER 2'],
            level=level,
            id=get_game_id(level, row + 2)
        ))
    return games


def create_game(level: int, player1: str, player2: str, player3: str) -> str:
    """Create a game."""
    sheet = get_sheet(level=level)
    empty = False
    for row, host_name in enumerate(sheet.col_values(1)):
        if not host_name:
            empty = True
            break
    row += 1    # we want it to be 1 based
    if not empty:
        row += 1
        sheet.add_rows(1)
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row, 3)
    players = [player1, player2, player3]
    for cell, player in zip(cells, players):
        cell.value = player
    sheet.update_cells(cells)
    return get_game_id(level, row)


@cache
def find_game(level: int, *players: typing.Tuple[str]) -> int:
    """Find which row a game is on."""
    sheet = get_sheet(level=level)
    found = False
    grid = sheet.get_all_values()
    for n, row in enumerate(grid):
        if all((player in row) for player in players):
            found = True
            break
    if not found:
        return 0, DONT_CACHE
    else:
        return n + 1    # we want it to be 1 based


def eliminate_player(level: int, row: int, player: str) -> str:
    """Mark a player as eliminated."""
    sheet = get_sheet(level=level)
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row, 7)
    if not cells[0].value:
        return f'That game does not exist.'
    if cells[-1].value:
        cells[-2].value = player
        for other_cell in cells[:3]:
            if other_cell.value not in (cells[-1].value, player):
                cells[-3].value = other_cell.value
                break
        message = f'{player} was eliminated, {other_cell.value} wins!'
    else:
        cells[-1].value = player
        message = f'{player} was eliminated.'
    sheet.update_cells(cells)
    return message


def rematch_check(
        player1: str, player2: str, player3: str) -> typing.List[int]:
    """Check what levels a game exists on."""
    levels = []
    for level in range(10):
        if find_game(level, player1, player2, player3):
            levels.append(level)
    return levels


def get_game(level: int, row: int):
    """Get a game."""
    sheet = get_sheet(level=level)
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row, 7)
    if not cells[0].value:
        return None
    return Game(
        player1=cells[0].value,
        player2=cells[1].value,
        player3=cells[2].value,
        winner=cells[-3].value if cells[-3].value != 'UNFINISHED' else '',
        loser1=cells[-2].value,
        loser2=cells[-1].value,
        level=level,
        id=get_game_id(level, row)
    )
