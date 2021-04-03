"""Peewee ORM models."""
import peewee

from ..main import config


db = peewee.PostgresqlDatabase(
    config.DB_NAME,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT
)
db.execute_sql('CREATE EXTENSION IF NOT EXISTS intarray;')


class BaseModel(peewee.Model):
    """Base model to set default settings."""

    class Meta:
        """Peewee settings config."""

        use_legacy_table_names = False
        database = db
