import re
import datetime


def log(message, level):
    tstamp = datetime.datetime.now().strftime('%d/%m/%y %H:%M')
    with open('data/logs.txt', 'a') as f:
        f.write(f'{time} [{level.upper()}] {message}')


def fetch(level=None):
    lines = []
    try:
        with open('data/logs.txt') as f:
            for i in f:
                if i.strip():
                    if not level:
                        lines.append(i.strip())
                    m = re.match('([^ ]+[^ ]+) \[([A-Z_]+)\] (.+)$', i)
                    tstamp, lvl, message = m.groups()
                    if lvl == level.upper():
                        line.append(f'{tstamp} | {message}')
    except FileNotFoundError:
        return '```\n```'
    return '```\n' + '\n'.join(reversed(lines)) + '```'
