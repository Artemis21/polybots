"""Hastebin client."""
import requests


URL = 'https://hastebin.com'


def upload(data: str) -> str:
    """Upload some data to hastebin."""
    resp = requests.post(f'{URL}/documents', data=data)
    key = resp.json()['key']
    return f'{URL}/raw/{key}'
