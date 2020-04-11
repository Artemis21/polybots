from pymongo import MongoClient
import json

from utils.models import Model


class DivisionSpecificModel(Model):
    @classmethod
    def all_in_league(cls, league, season=None):
        s = {'league': league}
        if season:
            s['season'] = season
        return cls.all(s)

    @classmethod
    def all_in_division(cls, league, division, season=None):
        s = {'division': division, 'league': league}
        if season:
            s['season'] = season
        return cls.all(s)


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
            'kills': Kills(None)
        }
        obj = super().create(data)
        obj.kills.game = obj
        return obj

    def __init__(self, id, data):
        data['kills'] = Kills(self, data['kills'])
        super().__init__(id, data)

    def __setattr__(self, name, value):
        if name == 'kills':
            value = {str(i): value[i] for i in value}
        super().__setattr__(name, value)


class Kills(dict):
    def __init__(self, game, dict_={}):
        self.game = game
        super().__init__(dict_)

    def __getitem__(self, key):
        return super().__getitem__(str(key))

    def __setitem__(self, key, value):
        super().__setitem__(str(key), value)
        self.game.kills = self

    def __iter__(self):
        for key in super().__iter__():
            yield int(key)

    def keys(self):
        for key in super().keys():
            yield int(key)

    def __str__(self):
        return '<Kills {}>'.format(super().__repr__())

    def __repr__(self):
        return str(self)


class Settings:
    FIELDS = {
        'admin_users': [496381034628251688],    # Artemis#8799
        'admin_roles': [],
        'banned_users': [],
        'banned_roles': [],
        'season': 2,
        'leagues': 3,
    }

    @classmethod
    def load(cls):
        try:
            with open('data/settings.json') as f:
                cls.data = json.load(f)
        except FileNotFoundError:
            cls.data = {}

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
