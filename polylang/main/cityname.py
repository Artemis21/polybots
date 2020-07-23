import random


LANGS = {
    'xinxi': ('xi', 'bu', 'li', 'yo', '-', 'sha', 'cha', 'szu', 'gu', 'po'),
    'imperius': (
        'mo', 'nu', 'pi', 'ca', 'te', 'ro', 'lus', 'mus', 'ica', 'lo', 're',
        'ma', 'ip', 'sum', 'do', 'res'
        ),
    'bardur': (
        'gu', 'lak', 'rø', 'bu', 'tof', 'fla', 'ork', 'gru', 'lin', 'ark', 'ur'
        ),
    'oumaji': ('on', 'dor', 'ye', 'ke', 'ba', 'ji', 'ha', 'la', 'si', 'gh',
        'lim', 'mu'
        ),
    'kickoo': (
        'lu', 'va', 'si', 'ma', 'an', 'nu', ' ', 'li', 'ko', 'oki', 'lo', 'ko',
        'no'
        ),
    'hoodrick': (
        'lo', 'in', 'ber', 'th', 'ol', 'go', 'we', 'don', 'ry', 'ick', 'ley',
        'wa'
        ),
    'luxidoor': (
        'em', 'ux', 'lô', 'ga', 'pô', 'exi', 'uss', 'ni', 'au', 'ou', 'ly',
        'iss', "'", 'ki'
        ),
    'vengir': (
        'bu', 'rz', 'gor', 'cth', 'xas', 'th', 'ar', 'ck', 'he', 'im',
        'pe', 'st', 'na', 'nt', 'dis', 'tu', 'rot'
        ),
    'zebasi': ('zu', 'za', 'bo', 'zan', 'la', 'mo', 'co', 'ya', 'wa', 'zim'),
    'aimo': (
        'lï', 'tï', 'pï', 'fï', 'nï', 'kï', 'sï', 'dee', 'lee', 'po', 'so',
        ' ', 'to'
        ),
    'aquarion': (
        'pol', 'at', 'tis', 'nép', 'tun', 'eid', 'lan', 'ico', 'in', 'po',
        'séi', 'do', 'aq', 'quo', 'tic', 'fic', 'nau'
        ),
    'quetzali': (
        'ya', 'tal', 'chu', 'ill', 'ca', 'ex', 'ja', 'was', ' el ', ' ', 'cho',
        'wop', 'qu', 'tz', 'tek', 'ix'
        ),
    'elyrion': (
        'Ŧo', 'Δ', '‡', 'þa', 'ȓ', 'ţe', 'πo', 'ƒi', '₼', '∑', '~', '¦', '₺',
        'ȱŋ'
        ),
    'yadakk': (
        'ül', 'tsa', 'ber', 'ki', 'st', 'ăn', 'ol', 'mer', 'kh', 'ar', 'üm',
        'tja', 'ge', 'urk', 'ark', 'az', 'gy', 'ug', 'sh', 'kă', 'kol', 'sam',
        'ez'
        ),
    'polaris': ('pol', "'il", 'iq', 'aa', 'nuu', 'pi', 'do', 'ta', 'an', 'to')
}


def alphabet(lang=''):
    name, lang = getlang(lang)
    letters = ''.join(sorted(set(''.join(lang))))
    syllables = ', '.join(sorted(lang))
    return f'{name} letters: {letters}\n{name} syllables: {syllables}'


def city(lang='', number=1):
    tribe, lang = getlang(lang)
    names = []
    for _ in range(number):
        name = ''
        while len(name) < random.randrange(3, 8):
            name += random.choice(lang)
            if name[0] in (' ', '-'):
                name = ''
        names.append(f'{tribe}: {name[0].upper()}{name[1:]}')
    return '\n'.join(names)


def getlang(search):
    if search:
        for name in LANGS:
            if search.lower().replace('-', '') in name:
                return name, LANGS[name]
    name = random.choice(list(LANGS.keys()))
    return name, LANGS[name]
