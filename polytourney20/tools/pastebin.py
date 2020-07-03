"""Termbin client."""
import requests
import json


URL = 'https://www.pastery.net/api/paste/'

with open('config.json') as f:
    data = json.load(f)
    KEY = data['pastery_key']


def upload(data: str) -> str:
    """Upload some data to termbin."""
    resp = requests.post(
        URL, data=data.encode(), params={'language': 'text', 'api_key': KEY}
    )
    return resp.json()['url'] + 'raw'
