from models.users import Users
from models.config import Config
from models.games import Games
from models.modifiers import Modifiers
from models.modes import Modes


models = (Config, Modes, Games, Users, Modifiers)


def load(bot):
    for model in models:
        model.load(bot)


def save():
    for model in models:
        model.save()
