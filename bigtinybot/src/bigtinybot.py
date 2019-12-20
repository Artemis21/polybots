import logging
import platform
from bot import BigTinyBot
import sys


with open('TOKEN') as f:
    key = f.read().strip()

if platform.dist()[0] == 'debian':
    pre = '~'
    token = key
    test = True
else:    # PRODUCTION MODE
    pre = '~'
    token = key
    test = False

logging.basicConfig(level=logging.INFO)


def run(cogs=[]):
    bot = BigTinyBot(prefix=pre, test=test, cogs=cogs)
    bot.run(token)


if __name__ == '__main__':
    run(sys.argv[1:])
