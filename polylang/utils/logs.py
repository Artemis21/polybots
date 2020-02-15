import re
import datetime


def log(message, level):
    tstamp = datetime.datetime.now().strftime('%d/%m/%y %H:%M')
    with open('data/logs.txt', 'a') as f:
        f.write(f'{tstamp} [{level.upper():^7}] {message}\n')


def fetch(level=None):
    lines = []
    try:
        with open('data/logs.txt') as f:
            for i in f:
                if i.strip():
                    if not level:
                        lines.append(i.strip())
                        continue
                    m = re.match('([^ ]+ [^ ]+) \[ *([A-Z_]+)\ *] (.+)$', i)
                    tstamp, lvl, message = m.groups()
                    if (not level) and (lvl != 'WINS'):
                        lines.append(i.strip())
                        continue
                    if lvl == level.upper():
                        lines.append(f'{tstamp} | {message}')
    except FileNotFoundError:
        return '```\n```'
    return '```\n' + '\n'.join(reversed(lines)) + '```'
