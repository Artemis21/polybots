"""Termbin client."""
import requests
import json


URL = 'https://hastebin.com/documents'


def upload(data: str) -> str:
    """Upload some data to hastebin."""
    resp = requests.post(URL, data=data.encode()).json()
    print(json.dumps(resp, indent=4))
    return 'https://hastebin.com/raw/' + resp['key']
