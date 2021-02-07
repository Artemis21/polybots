"""Migration to add extra fields to user profiles (07/02/21)."""
from playhouse.migrate import migrate, SqliteMigrator

from main.models import Player


def apply(migrator: SqliteMigrator):
    """Add extra fields to user profiles."""
    migrate(
        migrator.add_column('player', 'in_game_name', Player.in_game_name),
        migrator.add_column('player', 'utc_offset', Player.utc_offset),
        migrator.add_column('player', 'tribes', Player.tribes)
    )
