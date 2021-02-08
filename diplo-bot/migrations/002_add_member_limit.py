"""Migration to add a member limit field to games."""
from playhouse.migrate import migrate, SqliteMigrator

from main.models import Game


def apply(migrator: SqliteMigrator):
    """Add a member limit field to the game table."""
    migrate(migrator.add_column('game', 'limit', Game.limit))
