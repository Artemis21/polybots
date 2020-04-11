from pymongo import MongoClient

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
    def create(cls, id, name, code, division, league=4, points=0):
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
    def create(cls, host, division, league, season):
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


def setup():
    db = MongoClient().giant
    User.collection = db.users
    Game.collection = db.games
