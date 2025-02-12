"""Migration to add extra fields to user profiles (07/02/21)."""

from main.models import Player
from playhouse.migrate import SqliteMigrator, migrate


def apply(migrator: SqliteMigrator):
    """Add extra fields to user profiles."""
    migrate(
        migrator.add_column("player", "in_game_name", Player.in_game_name),
        migrator.add_column("player", "utc_offset", Player.utc_offset),
        migrator.add_column("player", "tribes", Player.tribes),
    )
