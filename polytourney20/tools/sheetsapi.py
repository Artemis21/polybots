"""Tools for interacting with the spreadsheet."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import typing
from collections import namedtuple


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
        'third'
    ]
)

player_cache = []
player_search_cache = {}
sheet_cache = {}


def get_sheet(
        name: typing.Optional[str] = None, *,
        level: typing.Optional[int] = None
        ) -> typing.Optional[gspread.Worksheet]:
    """Get a spreadsheet, using caching."""
    global sheet_cache
    if level is not None:
        name = f'Level {level}'
    if name in sheet_cache:
        return sheet_cache[name]
    sheet = spread_sheet.worksheet(name)
    sheet_cache[name] = sheet
    return sheet


def get_players() -> typing.List[Player]:
    """Get a list of every user."""
    sheet = get_sheet('Player Hub')
    records = sheet.get_all_records(head=6)
    players = []
    for record in records:
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
            third=record['3rd'] or 0
        ))
    return players


def search_player(
        searches: typing.List[str], use_cache: bool = True
        ) -> typing.List[Player]:
    """Search for a player.
    
    This can be by discord user, or a search for discord name /
    polytopia name / friend code. If use_cache is True, attempt
    to find the player in the cache before updating the cache and
    trying again if they are not found.
    """
    global player_cache, player_search_cache
    for search in searches:
        if search in player_search_cache:
            return player_search_cache[search]
    searches = [search.lower() for search in searches]
    possible = []
    if not use_cache:
        player_cache = get_players()
    for player in player_cache:
        fields = (
            player.discord_name, player.polytopia_name, player.friend_code
        )
        for field in fields:
            added = False
            for search in searches:
                if search in field.lower():
                    possible.append(player)
                    added = True
                    break
            if added:
                break
    if (not possible) and use_cache:
        return search_player(searches, False)
    for search in player_search_cache:
        player_search_cache[search] = possible
    return possible


def create_game(level: int, player1: str, player2: str, player3: str):
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
    cells = sheet.range(row, 1, row, 3)
    players = [player1, player2, player3]
    for cell, player in zip(cells, players):
        cell.value = player
    sheet.update_cells(cells)


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
        return 0
    else:
        return n + 1    # we want it to be 1 based


def set_result(level: int, winner: str, loser1: str, loser2: str) -> bool:
    """Set the result of a game."""
    sheet = get_sheet(level=level)
    row = find_game(level, winner, loser1, loser2)
    if not row:
        return False
    cells = sheet.range(row, 1, row, 5)
    players = [winner, loser1, loser2]
    for cell, player in zip(cells, players):
        cell.value = player
    sheet.update_cells(cells)
    return True


def rematch_check(
        player1: str, player2: str, player3: str) -> typing.List[int]:
    """Check what levels a game exists on."""
    levels = []
    for level in range(10):
        if find_game(level, player1, player2, player3):
            levels.append(level)
    return levels


def transpose_games():
    """Transpose the games sheets."""
    for n in range(10):
        sheet = get_sheet(level=n)
        data = sheet.get_all_values('FORMULA')
        print(data, '\n\n')
        new_data = list(map(list, zip(*data)))
        sheet.resize(rows=len(new_data), cols=len(new_data[0]))
        sheet.update(new_data, raw=True)
