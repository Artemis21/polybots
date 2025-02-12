"""Migration to add support for steam games."""

from main.models import Game, Player
from playhouse.migrate import SqliteMigrator, migrate


def apply(migrator: SqliteMigrator):
    """Add extra fields to user profiles."""
    migrate(
        migrator.rename_column("player", "in_game_name", "mobile_name"),
        migrator.add_column("player", "steam_name", Player.steam_name),
        migrator.add_column("game", "is_steam", Game.is_steam),
        # Not related but happened in the same update, for consistency and
        # clarity, and to avoid conflict with the builtin of the same name.
        migrator.rename_column("game", "open", "is_open"),
    )
