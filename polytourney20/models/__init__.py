"""Load all the data models."""
import discord

from models.config import Config    # noqa:F401


# my generic bot template, we don't actually have any SQL models
SQL_MODELS = []


def setup(bot: discord.Client):
    """Load models and perform other setup tasks."""
    for model in SQL_MODELS:
        model.ensure_table()
