import json


class Config:
    @classmethod
    def load(cls, bot):
        try:
            with open('data/config.json') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        cls.prefix = data.get('prefix', '&')
        cls.guild = bot.get_guild(data.get('guild', 570621740653477898))
        cls.game_cat = cls.guild.get_channel(
            data.get('cat', 638533642934812722)
        )
        cls.tiers = {}
        tiers = data.get('tiers', {})
        for points in tiers:
            cls.tiers[int(points)] = cls.guild.get_role(tiers[points])
        cls.announce = bot.get_channel(
            data.get('announce', 632002858102947840)
        )
        cls.notify = cls.guild.get_role(data.get('notify', 631991693230735362))

    @classmethod
    def get_prefix(cls, bot, message):
        return cls.prefix

    @classmethod
    def get_tier(cls, points):
        levels = sorted(list(cls.tiers.keys()), reverse=True)
        for level in levels:
            if level <= points:
                return cls.tiers[level]

    @classmethod
    def save(cls):
        data = {
            'prefix': cls.prefix,
            'guild': cls.guild.id,
            'tiers': {points: cls.tiers[points].id for points in cls.tiers},
            'announce': cls.announce.id,
            'notify': cls.notify.id
        }
        with open('data/config.json', 'w') as f:
            json.dump(data, f)
