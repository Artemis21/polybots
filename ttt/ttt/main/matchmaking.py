"""Queries to assist in matchmaking."""
from __future__ import annotations

from dataclasses import dataclass

from peewee import JOIN, Expression, fn

from ..models import Game, GamePlayer, Player


def array_agg(expr: Expression) -> Expression:
    """Do array aggregation and instruct Peewee not to coerce."""
    return fn.ARRAY_AGG(expr, coerce=False)


@dataclass
class PlayerCompatibility:
    """Store measures of the compatibility of players."""

    # How many games have any of them already played together?
    shared_games: int
    # Can they all play a position they haven't before?
    new_positions: bool
    # Can they all play a position they've played only once before?
    almost_new_positions: bool
    # Are any of them from the same team?
    common_teams: bool


@dataclass
class PlayerGameData:
    """Store data on a player's position in a game."""

    game: Game
    position: int
    won: bool


@dataclass
class PlayerData:
    """Store data on games of various states a player has."""

    game_count: int
    in_progress_count: int
    games: list[PlayerGameData]


def _games_in_common(players: list[Player]) -> int:
    """Count how many games any of a list of players have shared."""
    player_ids = [player.discord_id for player in players]
    Member1 = GamePlayer.alias('member_1')
    Member2 = GamePlayer.alias('member_2')
    return len(Member1.select().join(Member2, JOIN.LEFT_OUTER, on=(
        (Member1.game == Member2.game)
        & (Member1.id != Member2.id)
    )).where(
        Member1.player_id.in_(player_ids),
        Member2.player_id.in_(player_ids)
    ).distinct(Member1.game))


def _positions_played(players: list[Player]) -> list[list[int]]:
    """Get a list of positions played for each player."""
    player_ids = [player.discord_id for player in players]
    records = GamePlayer.select(
        array_agg(GamePlayer.position).alias('positions')
    ).group_by(GamePlayer.player_id).where(
        GamePlayer.player_id.in_(player_ids)
    )
    return [record.positions for record in records]


def _unique_positions_possible(
        played_positions: list[list[int]], max_repeats: int = 1) -> bool:
    """Check if players can play in unique positions."""
    available_positions = [
        [pos for pos in range(1, 5) if played.count(pos) < max_repeats]
        for played in played_positions
    ]
    combinations = [[]]
    for player_positions in available_positions:
        new_combinations = []
        for old_combination in combinations:
            for position in player_positions:
                new_combinations.append([*old_combination, position])
        combinations = new_combinations
    player_count = len(played_positions)
    return any(
        len(set(combination)) == player_count
        for combination in combinations
    )


def _players_from_same_team(players: list[Player]) -> bool:
    """Check if any players come from the same team."""
    teams = []
    for player in players:
        if player.team in teams:
            return True
        if player.team:
            teams.append(player.team)
    return False


def player_compatibility(players: list[Player]) -> PlayerCompatibility:
    """Calculate measures of player compatibility."""
    played_positions = _positions_played(players)
    return PlayerCompatibility(
        shared_games=_games_in_common(players),
        new_positions=_unique_positions_possible(played_positions),
        almost_new_positions=_unique_positions_possible(
            played_positions, max_repeats=2
        ),
        common_teams=_players_from_same_team(players)
    )


def _player_wins_after(player: Player, games: int) -> int:
    """Find out how many wins a player had after some games."""
    count = 0
    for won in player.game_wins[:games]:
        if won is None:
            break
        count += won
    return count


def _player_is_waiting(player: Player, level: int) -> bool:
    """Check if a player is waiting for a game on a level."""
    series = None
    if player.total in (2, 3) and player.complete in (2, 3):
        series, series_wins = 1, _player_wins_after(player, 2)
    elif player.total in (4, 5) and player.complete in (4, 5):
        series, series_wins = 2, _player_wins_after(player, 4)
    if not series:
        return False
    if level < 3:
        return series_wins == level
    if player.complete == player.wins == 3:
        return True
    return series_wins > 2 and series == 2


def players_waiting_on_level(level: int) -> list[Player]:
    """Get all players that are waiting for games on a level."""
    total = fn.COUNT(GamePlayer.id).alias('total')
    complete = fn.COUNT(GamePlayer.id).filter(
        GamePlayer.won.is_null(False)).alias('complete')
    wins = fn.COUNT(GamePlayer.id).filter(GamePlayer.won).alias('wins')
    losses = fn.COUNT(GamePlayer.id).filter(GamePlayer.lost).alias('losses')
    in_progress = fn.COUNT(GamePlayer.id).filter(
        GamePlayer.won.is_null(True)).alias('in_progress')
    records = Player.select(
        Player,
        array_agg(GamePlayer.game_id).order_by(
            GamePlayer.ended_at).alias('game_ids'),
        array_agg(GamePlayer.won).order_by(
            GamePlayer.ended_at).alias('game_wins'),
        array_agg(GamePlayer.position).order_by(
            GamePlayer.ended_at).alias('game_positions'),
        total, complete, in_progress, wins, losses
    ).join(GamePlayer).group_by(Player).order_by(
        -total, -in_progress
    )
    waiting = []
    for record in records:
        if _player_is_waiting(record, level):
            waiting.append(record)
    return waiting
