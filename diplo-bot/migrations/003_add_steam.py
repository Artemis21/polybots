"""Migration to add support for steam games."""
from playhouse.migrate import migrate, SqliteMigrator

from main.models import Game, Player


def apply(migrator: SqliteMigrator):
    """Add extra fields to user profiles."""
    migrate(
        migrator.rename_column('player', 'in_game_name', 'mobile_name'),
        migrator.add_column('player', 'steam_name', Player.steam_name),
        migrator.add_column('game', 'is_steam', Game.is_steam),
        # Not related but happened in the same update, for consistency and
        # clarity, and to avoid conflict with the builtin of the same name.
        migrator.rename_column('game', 'open', 'is_open')
    )
