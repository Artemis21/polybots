import json
import random


class Modifiers:
    @classmethod
    def load(cls, bot):
        try:
            with open('data/mods.json') as f:
                raw = json.load(f)
        except FileNotFoundError:
            raw = {}
        cls.mods = raw.get('mods', [])

    @classmethod
    def tostr(cls, mod):
        name = mod['name']
        desc = mod['desc']
        turns = mod['turns'] or '∞'
        return f'**{name}**: {desc} *(lasts {turns} turns in scramble games)*'

    @classmethod
    def get(cls):
        mods = cls.mods or ['No modifiers found.']
        mod = random.choice(mods)
        return cls.tostr(mod)

    @classmethod
    def all(cls):
        n = 1
        t = ['All modifiers:']
        for mod in cls.mods:
            line = f'\n**({n})** {cls.tostr(mod)}'
            if len(t[-1] + line) > 2000:
                t.append('')
            t[-1] += line
            n += 1
        return t

    @classmethod
    def add(cls, name, desc, turns):
        cls.mods.append({
            'name': name,
            'desc': desc,
            'turns': turns,
        })

    @classmethod
    def rem(cls, num):
        del cls.mods[num - 1]

    @classmethod
    def edit(cls, num, field, new):
        cls.mods[num-1][field] = new

    @classmethod
    def save(cls):
        data = {'mods': cls.mods}
        with open('data/mods.json', 'w') as f:
            json.dump(data, f)
