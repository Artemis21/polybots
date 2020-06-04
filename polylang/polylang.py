import logging
import platform
from bot import PolyLang
import sys


with open('config/TOKEN') as f:
    key = f.read().strip()

pre = ';'
token = ''#key
test = False

logging.basicConfig(level=logging.INFO)


def run(cogs=[]):
    bot = PolyLang(prefix=pre, test=test, cogs=cogs)
    bot.run(token)


if __name__ == '__main__':
    run(sys.argv[1:])
