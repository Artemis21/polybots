"""Setup Peewee's connection to the database."""
import peewee

from ..main import config


db = peewee.SqliteDatabase(str(config.BASE_PATH / 'db.sqlite3'))


class BaseModel(peewee.Model):
    """Base model to set default settings."""

    class Meta:
        """Peewee settings."""

        database = db
        use_legacy_table_names = False
