import logging
import platform
from bot import ArenaBot
import sys
import json


with open('SECRETS.json') as f:
    keys = json.load(f)

if platform.dist()[0] == 'debian':
    pre = '~'
    token = keys['testing_key']
    test = True
else:    # PRODUCTION MODE
    pre = '~'
    token = keys['key']
    test = False

logging.basicConfig(level=logging.INFO)


def run(cogs=[]):
    bot = ArenaBot(prefix=pre, test=test, cogs=cogs)
    bot.run(token)


if __name__ == '__main__':
    run(sys.argv[1:])
