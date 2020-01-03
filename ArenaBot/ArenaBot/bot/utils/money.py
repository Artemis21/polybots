import requests
import json


TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiI2NDI0ODcxNjYxODU4OTc5'
    'ODUiLCJpYXQiOjE1NzMyNTEyNzd9.NuTdJHCgqXYB31yatlfLl5hEffumSWKLIFs_GE8mCIg'
)
URL = 'https://unbelievaboat.com/api/v1'


def chbal(uid, gid, am, reason=''):
    url = f'{URL}/guilds/{gid}/users/{uid}'
    params = {
        'cash': am,
        'reason': reason,
    }
    data = json.dumps(params)
    headers = {
        'Authorization': TOKEN,
    }
    res = requests.patch(url, data=data, headers=headers)


def getbal(uid, gid):
    url = f'{URL}/guilds/{gid}/users/{uid}'
    headers = {
        'Authorization': TOKEN,
    }
    res = requests.get(url, headers=headers)
    return res.json()['cash']
