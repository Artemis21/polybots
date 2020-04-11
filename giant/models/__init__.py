from pymongo import MongoClient

from .settings import Settings
from .user import User
from .game import Game


db = MongoClient().giant
User.collection = db.users
Game.collection = db.games
Settings.load()
