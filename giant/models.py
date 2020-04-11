from pymongo import MongoClient
import json

from utils.models import Model


class DivisionSpecificModel(Model):
    @classmethod
    def all_in_league(cls, league):
        return cls.all({'league': league})

    @classmethod
    def all_in_division(cls, league, division):
        return cls.all({'division': division, 'league': league})


class User(DivisionSpecificModel):
    @classmethod
    def create(
            cls, id: int, name: str, code: str, division: str,
            league: int = 4, points: int = 0
            ):
        data = {
            'league': league,
            'division': division,
            'points': points,
            'name': name,
            'code': code,
        }
        return super().create(data, id)


class Game(DivisionSpecificModel):
    @classmethod
    def create(cls, host: int, division: str, league: int, season: int):
        data = {
            'host': host,
            'division': division,
            'league': league,
            'season': season,
            'name': None,
            'status': 'not started',
            'kills': {}
        }
        super().create(data)


class Settings:
    FIELDS = {
        'admin_users': [],
        'admin_roles': [],
        'banned_users': [],
        'banned_roles': [],
        'season': 2,
        'leagues': 4,
        'divisions': 8
    }

    @classmethod
    def load(cls):
        with open('data/settings.json') as f:
            cls.data = json.load(f)

    @classmethod
    def __getattr__(cls, name):
        if name in cls.FIELDS:
            return cls.data.get(name, cls.FIELDS[name])
        raise AttributeError(f'No attribute named {name}.')

    @classmethod
    def __setattr__(cls, name, value):
        if name not in cls.FIELDS:
            raise AttributeError(f'{name} is not a defined field.')
        if isinstance(value, type(cls.FIELDS[name])):
            raise ValueError(f'Field {name} must be of type {type(value)}.')
        cls.data[name] = value
        with open('data/settings.json', 'w') as f:
            json.dump(cls.data, f)


def setup():
    db = MongoClient().giant
    User.collection = db.users
    Game.collection = db.games
    Settings.load()
