"""Migration to add a member limit field to games."""

from main.models import Game
from playhouse.migrate import SqliteMigrator, migrate


def apply(migrator: SqliteMigrator):
    """Add a member limit field to the game table."""
    migrate(migrator.add_column("game", "limit", Game.limit))
