import json


with open('config/settings.json') as f:
    data = json.load(f)


def admin(user):
    return user.id in data['admins']
