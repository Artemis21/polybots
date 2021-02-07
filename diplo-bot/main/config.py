"""Load the JSON config."""
import json
import pathlib


BASE_PATH = pathlib.Path(__file__).parent.parent

with open(str(BASE_PATH / 'config.json')) as f:
    _data = json.load(f)

PREFIX = _data['prefix']
TOKEN = _data['token']

OBSERVER_ROLE_ID = _data['observer_role']
