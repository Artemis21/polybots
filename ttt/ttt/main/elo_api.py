"""Wrapper for the ELO bot API."""
import dataclasses
import datetime
from typing import Any, Optional

import aiohttp

import dataclasses_json

from .config import ELO_BASE_URL, ELO_PASSWORD, ELO_USERNAME


session: Optional[aiohttp.ClientSession] = None


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class EloGameSide:
    """A side from a game returned by the API."""

    id: int
    side_name: Optional[str]
    size: int
    position: int
    win_confirmed: bool
    members: list[int]


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class EloGame:
    """A game object returned from the API."""

    id: int
    guild_id: int
    is_ranked: bool
    is_mobile: bool
    is_completed: bool
    is_confirmed: bool
    is_open: bool
    name: str
    notes: str
    winner: Optional[int]
    win_claimed_at: Optional[datetime.datetime]
    size: list[int]
    sides: list[EloGameSide]


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class EloUserTeam:
    """A team of a user object returned from the API."""

    name: str
    pro: bool
    hidden: bool


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class EloUser:
    """A user object returned from the API."""

    discord_id: int
    name: Optional[str]
    steam_name: Optional[str]
    mobile_name: Optional[str]
    legacy_elo: Optional[int]
    moonrise_elo: int
    is_banned: bool
    utc_offset: Optional[int]
    teams: dict[int, EloUserTeam]
    games: Optional[dict[int, list[int]]] = dataclasses.field(
        default_factory=dict
    )


@dataclasses_json.dataclass_json
@dataclasses.dataclass()
class NewEloGame:
    """A game to be created via the API."""

    game_name: str
    guild_id: int
    sides_discord_ids: list[list[int]]
    notes: str = ''
    is_ranked: bool = False
    is_mobile: bool = True


class EloApiError(Exception):
    """An error returned by the API."""

    def __init__(self, code: int, message: str):
        """Store the code and message."""
        self.code = code
        self.message = message
        super().__init__(f'{code} - {message}')


async def get_session() -> aiohttp.ClientSession:
    """Get the AIOHTTP session, or create one if we don't have one yet."""
    global session
    if (not session) or session.closed:
        session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(
            ELO_USERNAME, ELO_PASSWORD
        ))
    return session


async def process_response(
        response: aiohttp.ClientResponse) -> dict[str, Any]:
    """Process a response from the API."""
    if response.status == 500:
        raise EloApiError(500, 'Internal server error.')
    data = await response.json()
    if response.status < 400:
        return data
    else:
        raise EloApiError(response.status, data['detail'])


async def get_game(elo_bot_id: int) -> EloGame:
    """Get a game by ELO bot ID."""
    session = await get_session()
    async with session.get(f'{ELO_BASE_URL}/games/{elo_bot_id}') as res:
        data = await process_response(res)
        return EloGame.from_dict(data)


async def get_user(discord_id: int) -> EloUser:
    """Get ELO bot user data by Discord ID."""
    session = await get_session()
    async with session.get(f'{ELO_BASE_URL}/users/{discord_id}') as res:
        data = await process_response(res)
        return EloUser.from_dict(data)


async def new_game(game: NewEloGame) -> int:
    """Create a new game via the API (returns ID)."""
    session = await get_session()
    game = game.to_dict()
    async with session.post(f'{ELO_BASE_URL}/game/new', json=game) as res:
        data = await process_response(res)
        return data['game_id']
