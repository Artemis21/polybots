import json
# more imports at the end to avoid circular imports


class User:
    @classmethod
    def load(cls, data, bot):
        user = bot.get_user(data['user'])
        points = data['points']
        tz = data['tz']
        if data['game']:
            game = Games.games[data['game']]
        else:
            game = None
        code = data['code']
        return cls(user=user, points=points, tz=tz, game=game, code=code)

    @classmethod
    async def new(cls, user):
        points = 0
        tz = 'Not Set'
        game = None
        code = 'Not Set'
        u = cls(user=user, points=points, tz=tz, game=game, code=code)
        await user.add_role(u.tier)
        return u

    def __init__(self, user, points, tz, game, code):
        self.user = user
        self.__points = points
        self.tz = tz
        self.game = game
        self.code = code

    @property
    def tier(self):
        return Config.get_tier(self.points)

    @property
    def points(self):
        return self.__points

    async def give_points(self, points):
        old = Config.get_tier(self.points)
        self.__points += points
        new = Config.get_tier(self.points)
        if old != new and points > 0:
            member = await Config.guild.fetch_user(self.user.id)
            await member.add_roles(new, reason='Changed tier.')
            await member.remove_roles(old, reason='Changed tier.')
        else:
            for p in Config.tiers:
                if Config.tiers[p] == old:
                    self.__points = p

    def dump(self):
        if self.game:
            game = self.game.id
        else:
            game = None
        return {
            'user': self.user.id,
            'points': self.points,
            'tz': self.tz,
            'game': game,
            'code': self.code,
        }


class Users:
    @classmethod
    def load(cls, bot):
        try:
            with open('data/users.json') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        users = data.get('users', [])
        cls.users = []
        for user in users:
            cls.users.append(User.load(user, bot))

    @classmethod
    async def get_user(cls, member):
        for u in cls.users:
            if u.id == member.id:
                return u
        u = await User.new(member)
        cls.users.append(u)
        return u

    @classmethod
    def save(cls):
        data = {
            'users': [u.dump() for u in cls.users]
        }
        with open('data/users.json', 'w') as f:
            json.dump(data, f)


from models.games import Games
from models.config import Config
