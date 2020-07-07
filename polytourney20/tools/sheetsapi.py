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
spread_sheet = client.open('Polytopia Supreme Summer Skirmish Sheet')

Player = namedtuple(
    'Player',
    [
        'discord_name',
        'polytopia_name',
        'friend_code',
        'elo',
        'level',
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
            discord_name=str(record['Discord Name:']) or 'Not found',
            polytopia_name=str(record['Polytopia Name:']) or 'Not found',
            friend_code=str(record['Friend Code:']) or 'Not found',
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
            discord_name=str(record['Discord Name:']) or 'Not found',
            polytopia_name=str(record['Polytopia Name:']) or 'Not found',
            friend_code=str(record['Friend Code:']) or 'Not found',
            elo=record['ELO'] or 1000,
            level=record['Level:'] or 0,
            wins=record['Wins:'] or 0,
            losses=record['Losses'] or 0,
            total_games=record['Total Games'] or 0,
            games_in_progress=record['Games in Progress'] or 0,
            needs_games=record['Needs Games?'] != 'No',
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
        if not raw_game['Host']:
            continue
        games.append(Game(
            player1=str(raw_game['Host']),
            player2=str(raw_game['2nd Pick']),
            player3=str(raw_game['3rd Pick']),
            winner=str(raw_game['Winner']),
            loser1=str(raw_game['Loser 1']),
            loser2=str(raw_game['Loser 2']),
            level=level,
            id=get_game_id(level, row + 2)
        ))
    return games


def find_next_empty(sheet: gspread.Worksheet, needed: int = 1) -> int:
    """Find the next empty row on a level sheet."""
    grid = sheet.get_all_values()
    for n, row in enumerate(grid):
        if not any(row[:3]):
            if needed + n <= len(grid):
                return n + 1
            n -= 1
            break
    empty = len(grid) - n - 1
    sheet.add_rows(needed - empty)
    return n + 2


def create_game(level: int, player1: str, player2: str, player3: str) -> str:
    """Create a game."""
    sheet = get_sheet(level=level)
    row = find_next_empty(sheet)
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row, 3)
    players = [player1, player2, player3]
    for cell, player in zip(cells, players):
        cell.value = player
    sheet.update_cells(cells)
    return get_game_id(level, row)


def create_games(level: int, games: typing.List[typing.List[str]]):
    """Create multiple games."""
    sheet = get_sheet(level=level)
    row = find_next_empty(sheet, len(games))
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row + len(games), 3)
    cell_num = 0
    for game in games:
        for player in game:
            cells[cell_num].value = player
            cell_num += 1
    sheet.update_cells(cells)


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
    else:
        cells[-1].value = player
    sheet.update_cells(cells)
    return f'{player} was eliminated.'


def award_win(level: int, row: int, player: str) -> bool:
    """Mark a player as having won a game."""
    sheet = get_sheet(level=level)
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row, 7)
    if not cells[0].value:
        return f'That game does not exist.'
    cells[-3].value = player
    sheet.update_cells(cells)
    return f'{player} has won!'


def rematch_check(
        player1: str, player2: str, player3: str) -> typing.List[int]:
    """Check what levels a game exists on."""
    sheet = get_sheet('Rematch Check')
    in_cells = sheet.range('B4:D4')
    for cell, player in zip(in_cells, (player1, player2, player3)):
        cell.value = player
    sheet.update_cells(in_cells)
    out_cells = sheet.range('F4:O4')
    out_values = [cell.value for cell in out_cells]
    levels = []
    for level in range(10):
        if int(out_values[level]):
            levels.append(level)
    return levels


def get_game(level: int, row: int):
    """Get a game."""
    sheet = get_sheet(level=level)
    # pylint: disable=too-many-function-args
    cells = sheet.range(row, 1, row, 7)
    if not any(cell.value for cell in cells[:3]):
        return None
    return Game(
        player1=cells[0].value or '-',
        player2=cells[1].value or '-',
        player3=cells[2].value or '-',
        winner=cells[-3].value if cells[-3].value != 'UNFINISHED' else '',
        loser1=cells[-2].value,
        loser2=cells[-1].value,
        level=level,
        id=get_game_id(level, row)
    )
