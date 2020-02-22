from models.config import Config
from models.users import Users
from models.modes import Modes
from models.modifiers import Modifiers
from main.utils import announce
import discord
import json


class Game:
    @classmethod
    def load(cls, data):
        modifiers = data['modifiers']
        players = data['players']
        mode = Modes.get_mode(data['mode'])
        if data['tier']:
            tier = Config.guild.get_role(data['tier'])
        else:
            tier = None
        if data['channel']:
            channel = Config.guild.get_channel(data['channel'])
        else:
            channel = None
        id = data['id']
        return cls(
            modifiers=modifiers, players=players, mode=mode, tier=tier, id=id,
            channel=channel
        )

    @classmethod
    def new(cls, mode, tier, id):
        return cls(
            modifiers=[], players=[], mode=mode, tier=tier, id=id, channel=None
        )

    def __init__(self, modifiers, players, mode, tier, id, channel):
        self.modifiers = modifiers
        self.players = players
        self.mode = mode
        self.tier = tier
        self.id = id
        self.channel = channel

    async def add_player(self, user):
        if self.tier:
            if self.tier not in user.roles:
                return f'You must have the {self.tier} role to join this game.'
        player = Users.get_user(player)
        if user.id in [i.id for i in self.players]:
            return 'You\'re already in this game!'
        if player.game:
            return f'You\'re already in game {player.game}!'
        player.game = self
        self.players.append(user)
        if self.open:
            await self.start()
        return 'Done!'

    async def start(self):
        await announce('Game started!', self.display())
        p = discord.PermissionOverwrite
        overwrites = {
            Config.guild.default_role: p(send_messages=False)
        }
        for player in self.players:
            overwrites[player] = p(send_messages=True)
        for role in Config.mod_roles:
            overwrites[role] = p(send_messages=True)
        self.channel = await Config.guild.create_text_channel(
            str(self), category=Config.game_cat, overwrites=overwrites
        )
        await self.channel.send(
            f'Game Started!\n{self.players[0].mention} should now create the '
            'game. The game codes will be listed below, in the order that '
            'players should be added. Modifiers should not be chosen until '
            'each player has joined the game.',
            embed=self.display()
        )
        for users in zip(*self.teams):
            for user in users:
                player = Users.get_user(user)
                await self.channel.send(f'Friend code for {user.mention}:')
                await self.channel.send(f'`{player.code}`')

    def modifier(self):
        self.modifiers = []
        for _ in range(self.mode.mods):
            new = ''
            while (not new) or (new in self.modifiers):
                new = Modifiers.get()
            self.modifiers.append(new)
        return (
            '**Modifier/s:**\n' + '\n'.join(self.modifiers)
            + '\n\nIf these modifiers are incompatible with each other or '
              'previous modifiers, just run the command again.'
        )

    async def end(self, winner):
        if winner < self.mode.teams:
            return (
                'Winner must be a team number between 1 and '
                f'{self.mode.teams}.'
            )
        for n, team in enumerate(self.teams):
            players = [Users.get_user(i) for i in team]
            if n+1 == winner:
                winners = team
                for p in players:
                    p.give_points(self.mode.win)
            else:
                for p in players:
                    p.give_points(-self.mode.loss)
            for p in players:
                p.game = None
        pings = ' | '.join(i.mention for i in winners)
        await announce(f'Game ended, congratz {pings}!', self.display())
        await self.channel.delete()
        del Games.games[self.id]

    async def delete(self):
        if self.channel:
            await self.channel.delete()
        for u in self.players:
            p = Users.get_user(u)
            p.game = None
        del Games.games[self.id]

    @property
    def teams(self):
        teams = [[]]
        n = 0
        for player in self.players:
            teams[-1].append(player)
            n += 1
            if n == self.mode.players:
                n = 0
                teams.append([])
        return teams

    @property
    def open(self):
        return len(self.players) < self.mode.players * self.mode.teams

    def display(self):
        desc = ('In Progress', 'Open')[self.open]
        e = discord.Embed(title=self, description=desc)
        if self.tier:
            e.add_field(name='Tier', value=self.tier.mention)
        if self.channel:
            e.add_field(name='Channel', value=self.channel.mention)
        if self.modifiers:
            e.add_field(name='Modifiers', value='\n'.join(self.modifiers))
        e.add_field(name='Mode', value=self.mode)
        for n, team in enumerate(self.teams):
            pings = ' | '.join(i.mention for i in teams)
            e.add_field(name=f'Team {n+1}', value=pings)
        return e

    def __str__(self):
        return f'{self.mode.name}-{self.id}'

    def dump(self):
        if self.tier:
            tier = self.tier.id
        else:
            tier = None
        if self.channel:
            channel = channel.id
        else:
            channel = None
        return {
            'modifiers': self.modifiers,
            'players': [i.id for i in self.players],
            'mode': self.mode,
            'tier': tier,
            'channel': channel,
            'id': self.id,
        }


class Games:
    @classmethod
    def load(cls, bot):
        try:
            with open('data/games.json') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        cls.nextid = data.get('next', 0)
        cls.games = {}
        for game in data.get('games', []):
            g = Game.load(game)
            cls.games[g.id] = g

    @classmethod
    def get(self, channel):
        for id in cls.games:
            if cls.games[id].channel.id == channel.id:
                return cls.games[id]

    @classmethod
    def new(self, mode, tier):
        g = Game.new(mode, tier, cls.nextid)
        cls.games[cls.nextid] = g
        cls.nextid += 1
        return g

    @classmethod
    def save(cls):
        data = {
            'next': cls.nextid,
            'games': [g.dump() for g in cls.games.values()],
        }
        with open('data/games.json', 'w') as f:
            json.dump(data, f)
