from discord.ext import commands
import discord
import random
import math
import time
import string
import json
import typing
from utils.paginator import DescPaginator as Paginator
from utils.colours import colours
from utils.money import chbal


class Settings:
    @classmethod
    def load(cls):
        if bot.test:
            guild = 640606716442050605
            mod = 643176667900280863
            cat = 641058883825303562
            alert = 643176941733543977
            notif = 643176980862468124
            cls.symbol = '<:octagon:643177966213267456>'
        else:
            guild = 570621740653477898
            mod = 613206229283766273
            cat = 638533642934812722
            alert = 632002858102947840
            notif = 631991693230735362
            cls.symbol = '<:Currency:584210115864035348>'
        cls.guild = bot.get_guild(guild)
        cls.mod = cls.guild.get_role(mod)
        cls.notif = cls.guild.get_role(notif)
        cls.cat = cls.guild.get_channel(cat)
        cls.alert = cls.guild.get_channel(alert)
        cls.modes = (
            Mode('regular', 2, 1, 1, False, 5, 4),
            Mode('double', 2, 1, 2, False, 6, 4),
            Mode('skirmish3', 2, 3, 1, False, 8, 5),
            Mode('skirmish5', 2, 5, 1, False, 8, 5),
            Mode('rumble4', 4, 1, 1, False, 10, 2),
            Mode('rumble8', 8, 1, 1, False, 10, 2),
            Mode('scramble3', 3, 1, 1, True, 9, 2),
            Mode('scramble4', 4, 1, 1, True, 9, 2),
            Mode('scramble6', 6, 1, 1, True, 9, 2),
        )
        cls.nums = {
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
            6: 'six',
            7: 'seven',
            8: 'eight',
            9: 'nine',
            10: 'ten',
        }


class Utils:
    '''
    Assorted utility functions.
    '''
    @staticmethod
    async def notify(msg):
        '''
        Send a message in #arena-alerts, pinging @Notify.
        '''
        await Settings.alert.send(Settings.notif.mention + '\n' + msg)

    @staticmethod
    def pretty_mods(mods):
        '''
        Display format a list of modifiers.
        '''
        one = '{}{}: {:<20.20}'
        line = True
        text = ''
        n = 1
        for i in mods:
            text += one.format(('|', '\n')[line], n, i)
            line = not line
            n += 1
        return '```' + (text[1:] or '[no modifiers found]') + '```'

    @staticmethod
    def mod_check():
        '''
        Command check for sultan role.
        '''
        async def ret(ctx):
            return Settings.mod in ctx.author.roles
        return commands.check(ret)


class Mode:
    '''
    A game mode. See __init__.
    '''
    @staticmethod
    def convert(arg):
        '''
        Convert a game mode as command parameter.
        '''
        for i in Settings.modes:
            if i.name == arg.lower():
                return i
        raise commands.BadArgument(
                f'Invalid game mode `{arg}`. Please see the `modes` command'
                ' for a list.'
        )

    def __init__(
            self, name, teams, team_size, mods, round_mods, win_pts, loss_pts
            ):
        '''
        A game mode. Params:
         - name: unique name with no spaces (str)
         - teams: number of teams (int)
         - team_size: players per team (int)
         - mods: number of modifiers (int)
         - round_mods: new mods each turn (bool)
         - win_pts: points awarded for a win (int)
         - los_pts: points deducted for a loss (int)
        '''
        self.name = name
        self.teams = teams
        self.team_size = team_size
        self.mods = mods
        self.round_mods = round_mods
        if round_mods:
            self.get_mod = ModData.get_rot
        else:
            self.get_mod = ModData.get
        self.win = win_pts
        self.loss = loss_pts

    def main_str(self):
        '''
        Main part of the descriptor. Looks like \
        "2 modifiers per game, 5 player FFA".
        '''
        if self.team_size > 1:
            teams_part = (
                f'{Settings.nums[self.teams]} teams of '
                f'{Settings.nums[self.team_size]}'
            )
        elif self.teams > 4:
            teams_part = f'{Settings.nums[self.teams]} player FFA'
        else:
            teams_part = ('1v' * self.teams)[:-1]
        s = ''
        if self.mods - 1:
            s = 's'
        per = ('game', 'round')[self.round_mods]
        mods = Settings.nums[self.mods].title()
        win = Settings.nums[self.win]
        loss = Settings.nums[self.loss]
        return (
            f'{mods} modifier{s} per {per}, {teams_part}. Win: {win} points; '
            f'loose: {loss} points.'
        )

    def __str__(self):
        '''
        Format for game info.
        '''
        return '{} ({})'.format(self.name, self.main_str())

    def for_list(self):
        '''
        Format for mode list.
        '''
        return '{:^9}: {:^35.35}'.format(self.name, self.main_str())

    def pick_mods(self, avoid=()):
        '''
        Pick modifiers according to rules.
        '''
        mods = self.get_mod()
        if len(mods) == 0:
            return ('[no modifiers found]',)
        if len(mods) == 1:
            return (mods[0],)
        pos_mods = tuple(i for i in mods if i not in avoid)
        return random.choices(pos_mods, k=self.mods)


class Game:
    @staticmethod
    def get_id():
        '''
        Get a unique ID.
        '''
        n = math.floor(time.time())
        chars = string.digits + string.ascii_letters
        ret = ''
        while n > 0:
            n, i = divmod(n, 36)
            ret = chars[i] + ret
        return ret

    @classmethod
    async def create(cls, mode, lock):
        '''
        Constructor: create a game with starting values.
        '''
        winner = 0
        claims = {}
        mods = None
        id = Game.get_id()
        status = 'open'
        users = []
        channel = None
        bets = {}
        can_bet = True
        locked = ''
        if lock:
            locked = f' locked to players with the {lock} role'
        await Utils.notify(
            f':new:A new {mode.name} game (ID {id}) has been started{locked}! '
            f'Use `{bot.command_prefix}join {id}` to join it.'
        )
        return cls(
            channel, users, mode, claims, winner, id, mods, status, lock, bets,
            can_bet
        )

    @classmethod
    def load(cls, data):
        '''
        Constructor: load a game from saved data.
        '''
        channel = bot.get_channel(data['channel'])
        users = tuple(bot.get_user(i) for i in data['users'])
        mode = Mode.convert(data['mode'])
        claims = data['claims']
        winner = data['winner']
        id = data['id']
        mods = data['mods']
        status = data['status']
        lock = Settings.guild.get_role(data['lock'])
        bets = data['bets']
        can_bet = data['can_bet']
        return cls(
            channel, users, mode, claims, winner, id, mods, status, lock, bets,
            can_bet
        )

    def dump(self):
        '''
        Return data as dict to be dumped to json.
        '''
        data = {
            'channel': getattr(self.channel, 'id', 0),
            'users': [i.id for i in self.players],
            'mode': self.mode.name,
            'claims': self.claims,
            'winner': self.winner,
            'id': self.id,
            'mods': self.mods,
            'status': self.status,
            'lock': getattr(self.channel, 'id', 0),
            'bets': self.bets,
            'can_bet': self.can_bet,
        }
        return data

    def __init__(
            self, channel, users, mode, claims, winner, id, mods, status, lock,
            bets, can_bet
            ):
        '''
        Should not be used - use contructors load or create instead.
        '''
        self.channel = channel
        self.mode = mode
        self.players = list(users)
        self.claims = claims
        self.winner = winner
        self.status = status
        self.id = id
        self.mods = mods
        self.lock = lock
        self.bets = bets
        self.can_bet = can_bet

    async def delete(self):
        if self.channel:
            try:
                await self.channel.delete(reason='Game deleted.')
            except Exception:
                pass

    @property
    def teams(self):
        '''
        Get a 2d list of teams.
        '''
        ret = []
        users = self.players[:]
        for num in range(self.mode.teams):
            team = []
            for p in range(self.mode.team_size):
                try:
                    u = users.pop(0)
                except IndexError:
                    u = None
                team.append(u)
            ret.append(team)
        return ret

    @property
    def info(self):
        '''
        Get a discord embed with game details.
        '''
        e = discord.Embed(title=f'Game {self}', colour=colours['blue'])
        e.add_field(name='Mode', value=self.mode)
        if seld.mods:
            ms = '; '.join(self.mods)
            e.add_field(name='Modifiers', value=ms)
        if self.channel:
            e.add_field(name='Channel', value=self.channel.mention)
        if self.lock:
            e.add_field(name='Role lock', value=self.lock.mention)
        n = 1
        for t in self.teams:
            val = ', '.join((getattr(i, 'mention', '[vacant]') for i in t))
            name = f'Team {n}'
            e.add_field(name=name, value=val, inline=False)
            n += 1
        if self.winner:
            e.add_field(name='Winner', value=f'Team {self.winner}')
        if self.claims and not self.winner:
            s = '{} claims win for team {}.'
            val = '\n'.join(s.format(i, self.claims[i]) for i in self.claims)
            e.add_field(name='Claims', value=val)
        if (not self.can_bet) and (self.status == 'ongoing'):
            e.add_field(name='Betting Locked', value='​')    # ZWSP
        if self.bets:
            lines = []
            lfmt = '{} bets {}{} on team {}.'
            for better in self.bets:
                bt = bot.get_user(better)
                for team in self.bets[better]:
                    lines.append(
                        lmft.format(
                            bt, Settings.symbol, self.bets[better][team], team
                        )
                    )
            e.add_field(name='Bets', value='\n'.join(lines))
        return e

    def bet(self, user, team, amt):
        '''
        Register a user's bet.
        '''
        if self.status != 'ongoing':
            return 1, 'game is not ongoing'
        if not self.can_bet:
            return 1, 'betting has closed'
        if amt < 0:
            return 1, f'you cannot bet less than {Settings.symbol}0.'
        teams = self.teams
        if team < 1 or team > len(teams):
            return 1, f'there is no team {team}'
        if (user in self.players) and (user not in teams[team - 1]):
            return 1, 'you cannot bet on your opponents'
        bal = getbal(user)
        if bal < amt:
            return 1, f'you only have {Settings.symbol}{bal}'
        if user.id not in self.bets:
            self.bets[user.id] = {}
        self.bets[user.id][target.id] = amt
        chbal(user.id, Settings.guild.id, -amt, reason='Placed bet: deposit.')
        return 0, f'placed bet of {Settings.symbol}{amt} on {target}'

    def lock_bets(self):
        '''
        Lock bets (after T5 ss).
        '''
        if self.status != 'ongoing':
            return 1, 'game is not ongoing'
        self.can_bet = False
        return 0, 'betting disabled'

    async def adduser(self, user):
        '''
        Add a player.
        '''
        if user in self.players:
            return 1, 'user already added'
        if self.status != 'open':
            return 1, 'game is not open'
        if self.lock and self.lock not in user.roles:
            return 1, f'user has not got the {self.lock} role'
        for i in GameData.all():
            if user in i.players:
                return 1, f'user already in game {i}'
        self.players.append(user)
        if len(self.players) == self.mode.teams*self.mode.team_size:
            await self.begin()
            return 0, 'game started'
        return 0, 'added user'

    async def begin(self):
        self.status = 'ongoing'
        self.mods = self.mode.pick_mods()
        ch = await self.mk_ch()
        mes = ' | '.join(i.mention for i in self.players)
        await ch.send(mes, embed=self.info)
        await Utils.notify(
            f':triangular_flag_on_post:A {self.mode.name} match (ID '
            f'{self.id}) between {mes} has started in {ch.mention}!'
        )
        self.channel = ch

    async def mk_ch(self):
        '''
        Make the game channel upon starting.
        '''
        ps = {}
        ps[Settings.guild.default_role] = discord.PermissionOverwrite(
            send_messages=False
        )
        perm = discord.PermissionOverwrite(send_messages=True)
        for i in self.players:
            ps[i] = perm
        ps[Settings.mod] = perm
        name = f'{self.mode.name}-{self.id}'
        return await Settings.guild.create_text_channel(
            name, overwrites=ps, category=Settings.cat
        )

    def remuser(self, user):
        '''
        Remove a user from the game.
        '''
        if self.status != 'open':
            return 1, 'game is not open, too late'
        if user not in self.players:
            return 1, 'user not in this game'
        self.players.remove(user)
        return 0, 'removed user'

    def pickmods(self):
        '''
        Pick the modifiers for the next round of a scramble game.
        '''
        if self.status != 'ongoing':
            return False, 'game is not ongoing'
        if not self.mode.round_mods:
            return False, 'this is not a scramble game'
        self.mods = self.mode.pick_mods(self.channel.guild, self.mods)
        return True, self.info

    async def claimwin(self, user, team):
        '''
        Register a user's win claim.
        '''
        if self.status != 'ongoing':
            return 1, 'game is not ongoing'
        if user not in self.players:
            return 1, 'you are not in this game'
        if team < 1 or team > len(self.teams):
            return 1, 'invalid team number'
        self.claims[user.mention] = team
        totals = {}
        for i in self.claims:
            totals[self.claims[i]] = totals.get(self.claims[i], 0) + 1
        maj = math.floor(len(self.players)/2 + 1)
        for i in totals:
            if totals[i] >= maj:
                self.winner = i
                await self.end()
                break
        return 0, self.info

    async def mod_end(self, winner):
        '''
        Register a mod's win claim.
        '''
        if self.status != 'ongoing':
            return 1, 'game is not ongoing'
        if team < 1 or team > len(self.teams):
            return 1, 'invalid team number'
        self.winner = i
        await self.end()
        return 0, 'game ended'

    async def end(self):
        self.status = 'over'
        await Utils.notify(
            f':tada:Team {self.winner} won game ID {self.id} '
            f'({self.mode.name})!'
        )
        for uid in self.bets:
            for team in self.bets[uid]:
                if team == self.winner:
                    chbal(
                        uid, Settings.guild.id, self.bets[uid][team]*2,
                        'Won a bet.'
                    )

    def __str__(self): return str(self.id)


class Users:
    default = {
        'pts': 0,
        'tier': 1,
        'name': '[not given]',
        'code': '[not given]',
        'tz': '[not given]',
    }
    tiers = {
        1: 25,
        2: 30,
    }

    @classmethod
    def load(cls):
        with open('data/users.json') as f:
            cls.data = json.load(f)

    @classmethod
    def ensure(cls, user):
        cls.data[user] = cls.defualt

    @classmethod
    def get(cls, user):
        return cls.data.get(user.id, cls.default)

    @classmethod
    async def give_pts(cls, user, amt):
        self.ensure(user)
        cls.data[user.id]['pts'] += amt
        if cls.data[user.id]['pts'] < 0:
            cls.data[user.id]['pts'] = 0
        top = cls.tiers.get(cls.data[user.id]['tier'], None)
        if top and cls.data[user.id]['pts'] >= top:
            cls.data[user.id]['pts'] = 0
            cls.data[user.id]['tier'] += 1
            user


class ModData:
    @classmethod
    def load(cls):
        '''
        Load data from save.
        '''
        with open('data/mods.json') as f:
            cls.mods = json.load(f)

    @classmethod
    def get(cls):
        '''
        Get all the modifiers.
        '''
        cls.ensure()
        return cls.mods['mods']

    @classmethod
    def get_rot(cls):
        '''
        Get all the rotational modifiers.
        '''
        cls.ensure()
        return cls.mods['rot_mods']

    @classmethod
    def ensure(cls):
        '''
        Make sure the modifiers/rotational modifiers list exists.
        '''
        if 'mods' not in cls.mods:
            cls.mods['mods'] = []
        if 'rot_mods' not in cls.mods:
            cls.mods['rot_mods'] = []

    @classmethod
    def add(cls, mod):
        '''
        Add a modifier.
        '''
        cls.ensure()
        cls.mods['mods'].append(mod)

    @classmethod
    def add_rot(cls, mod):
        '''
        Add a rotational modifier.
        '''
        cls.ensure()
        cls.mods['rot_mods'].append(mod)

    @classmethod
    def rem(cls, num):
        '''
        Remove a modifier.
        '''
        cls.ensure()
        mx = len(cls.mods['mods'])
        if not 1 <= num <= mx:
            return False, f'number must be between 1 and {mx}'
        num -= 1
        mod = cls.mods['mods'].pop(num)
        return True, mod

    @classmethod
    def rem_rot(cls, num):
        '''
        Remove a rotational modifier.
        '''
        cls.ensure()
        mx = len(cls.mods['rot_mods'])
        if not 1 <= num <= mx:
            return False, f'number must be between 1 and {mx}'
        num -= 1
        mod = cls.mods['rot_mods'].pop(num)
        return True, mod

    @classmethod
    def clear(cls):
        '''
        Clear all the modifiers.
        '''
        cls.mods = {}

    @classmethod
    def save(cls):
        '''
        Save the modifiers to json.
        '''
        with open('data/mods.json', 'w') as f:
            json.dump(cls.mods, f)


class GameData:
    @classmethod
    def load(cls):
        '''
        Load data from save.
        '''
        with open('data/games.json') as f:
            data = json.load(f)
        cls.games = []
        for i in data:
            cls.games.append(Game.load(i))

    @classmethod
    async def new(cls, mode, lock):
        '''
        Begin a new game, return the game object.
        '''
        game = await Game.create(mode, lock)
        cls.games.append(game)
        return game

    @classmethod
    def get(cls, ch):
        '''
        Get a game ojbect by channel.
        '''
        for i in cls.games:
            if i.channel == ch:
                return i

    @classmethod
    def get_by_id(cls, id):
        '''
        Get a game ojbect by ID.
        '''
        for i in cls.games:
            if i.id == id:
                return i
        raise commands.CommandError('Game ID not found.')

    @classmethod
    def all(cls):
        '''
        Return every game.
        '''
        return cls.games

    @classmethod
    async def rem(cls, game):
        '''
        Remove a game object.
        '''
        await game.delete()
        cls.games.remove(game)

    @classmethod
    async def clear(cls):
        '''
        Remove every game object.
        '''
        for i in cls.games:
            await i.delete()
        cls.games = []

    @classmethod
    def save(cls):
        '''
        Save all game data to json.
        '''
        data = [i.dump() for i in cls.games]
        with open('data/games.json', 'w') as f:
            json.dump(data, f)


class Games(commands.Cog):
    '''
    The main features of the bot: creating and playing games!
    '''
    def __init__(self, bot_):
        '''
        Share global variable bot.
        '''
        global bot
        bot = bot_

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        Load data and get global discord entities.
        '''
        ModData.load()
        GameData.load()
        Settings.load()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, ch):
        '''
        Delete games if the channel is deleted.
        '''
        game = GameData.get(ch)
        if game:
            GameData.rem(game)
            GameData.save()

    async def use_ret(self, status, mes, ctx):
        '''
        Use the return status and message of a function to send a message to \
        ctx.
        '''
        args = {
            'content': ('Success: ', 'Error: ')[status]
        }
        if type(mes) == discord.Embed:
            args['embed'] = mes
        else:
            args['content'] += mes + '.'
        await ctx.send(**args)

    @commands.command(
        brief='Open a game.',
        description=(
            'Open a game. Parameters:\n'
            '   `mode`: a game mode, see `{{pre}}modes` for a list\n'
            '   `lock`: (optional) a role which all participants must have\n'
            'Examples:\n'
            '   `{{pre}}new double`\n'
            '   `{{pre}}new skirmish3 @base tier`\n'
            'Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def new(self, ctx, mode: Mode.convert,
                  lock: typing.Optional[discord.Role]):
        game = await GameData.new(mode, lock)
        await ctx.send('Game opened!', embed=game.info)
        GameData.save()

    @commands.command(
        brief='Join a game.',
        description=(
            'Use a game ID to join a game. You may only be in one game at '
            'once.'
        )
    )
    async def join(self, ctx, game: GameData.get_by_id):
        s, m = await game.adduser(ctx.author)
        await self.use_ret(s, m, ctx)
        GameData.save()

    @commands.command(
        brief='Leave your game.',
        description='Leave the game you are currently in, if any.'
    )
    async def leave(self, ctx):
        for i in GameData.all():
            if ctx.author in i.players:
                s, m = i.remuser(ctx.author)
                await self.use_ret(s, m, ctx)
                GameData.save()
                return
        await ctx.send('Error: not in a game.')

    @commands.command(
        brief='Get the next modifier.',
        description=(
            'Request a new modifier for a scramble game. This should only be '
            'used by the first player, but this is not enforced since they '
            'may die, leaving a new first player. This may only be used in '
            'a scramble game channel.'
        )
    )
    async def modifier(self, ctx):
        game = GameData.get(ctx.channel)
        if not game:
            return await ctx.send('There is no game in this channel.')
        if ctx.author not in game.players:
            return await ctx.send(f'You are not playing in game {game}.')
        if not game.mode.round_mods:
            return await ctx.send(f'{game} is not a scramble game.')
        if game.status != 'ongoing':
            return await ctx.send(f'{game} is not ongoing!')
        game.pickmods()
        await ctx.send('Modifier changed!', embed=game.info)
        GameData.save()

    @commands.command(
        brief='Find out about a game.',
        description=(
            'View the details of a game. If no game ID is provided, attempts '
            'to use the one in this channel.'
        )
    )
    async def info(self, ctx, game: typing.Optional[GameData.get_by_id]):
        if not game:
            game = GameData.get(ctx.channel)
            if not game:
                return await ctx.send('There is no game in this channel.')
        await ctx.send(embed=game.info)

    @commands.command(
        brief='End a game.',
        description=(
            'Mark this game as ended, specifying the team number which won. '
            'Once over half the players have done this (for the same team), '
            'the game will be marked as concluded. Incase of dispute, a '
            'sultan may also mark the game as over, which is final.'
        )
    )
    async def end(self, ctx, winner: int):
        game = GameData.get(ctx.channel)
        if not game:
            return await ctx.send('There is no game in this channel.')
        if await Utils.mod_check()(ctx):
            s, m = await game.mod_end(winner)
        elif ctx.author in game.players:
            s, m = await game.claim_win(ctx.author, winner)
        else:
            return ctx.send(f'You are not playing in game {game}.')
        await self.use_ret(s, m, ctx)
        GameData.save()

    @commands.command(
        brief='View all games.',
        description=(
            'View all currently open, ongoing and closed games in the server.'
        )
    )
    async def all(self, ctx):
        games = GameData.all()
        text = ''
        for i in games:
            text += '\n{:<6} | {:<9} | {:<5}'.format(
                i.id, i.mode.name, i.status
            )
        pag = Paginator(ctx, 'All Games', text[1:], pre='```', end='```')
        await pag.setup()

    @commands.command(
        brief='Delete a game.',
        description=(
            'Force a game to end. If no game ID is provided, attempts to use '
            'the one in this channel. Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def delete(self, ctx, game: typing.Optional[GameData.get_by_id]):
        if not game:
            game = GameData.get(ctx.channel)
            if not game:
                return await ctx.send('There is no game in this channel.')
        await ctx.send(
            f'Are you sure you want to delete game {game}? (`yes` to delete,'
            ' anything else to cancel)'
        )

        def check(mes):
            return (mes.author == ctx.author) and (mes.channel == ctx.channel)
        mes = await bot.wait_for('message', check=check)
        if mes.content.lower() != 'yes':
            return await ctx.send('Whew! That was close...')
        await game.delete()
        GameData.rem(game)
        GameData.save()
        await ctx.send(f'Game {game} deleted.')

    @commands.command(
        brief='Place a bet.',
        description=(
            'Place a bet on a game. New bets on the same user will override '
            'previous ones. Bet 0 to cancel your bet. A moderator will '
            'disable changing bets after the T5 screenshots. You may not bet '
            'on your opponents. Example usage: `{{pre}}bet 1000 2 abc123`: '
            'place a bet of 1000 on team 2 in game `abc123`.'
        )
    )
    async def bet(
            self, ctx, amount: int, team: int, game: GameData.get_by_id):
        s, m = game.bet(ctx.author, team, amount)
        await self.use_ret(s, m, ctx)
        GameData.save()

    @commands.command(
        brief='End betting.',
        description=(
            'Disable betting on a game. To be used by sultans after the T5 '
            'screenshots. `game` should be a game ID, leave blank for the '
            'game in this channel.'
        )
    )
    @Utils.mod_check()
    async def endbets(self, ctx, game: typing.Optional[GameData.get_by_id]):
        if not game:
            game = GameData.get(ctx.channel)
            if not game:
                return await ctx.send('There is no game in this channel.')
        s, m = game.lock_bets()
        await self.use_ret(s, m, ctx)
        GameData.save()

    @commands.command(
        brief='View the game modes.',
        description='View details of each game mode.'
    )
    async def modes(self, ctx):
        e = discord.Embed(title='Game Modes', color=colours['black'])
        for i in Settings.modes:
            e.add_field(name=i.name, value=i.main_str())
        await ctx.send(embed=e)


class Modifiers(commands.Cog):
    '''
    Create, delete and view the modifiers that will be used in games.
    '''
    def __init__(self, bot): pass

    @commands.command(
        brief='Add a permanent modifier.',
        description=(
            'Add a permanent modifier (one that stays the same the whole game)'
            '. Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def addmod(self, ctx, *, name):
        ModData.add(name)
        await ctx.send('Done!')
        ModData.save()

    @commands.command(
        brief='Add a rotational modifier.',
        description=(
            'Add a rotational modifier (one that changes every round). '
            'Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def addrotmod(self, ctx, *, name):
        ModData.add_mod(name)
        await ctx.send('Done!')
        ModData.save()

    @commands.command(
        brief='See all the modifiers.',
        description='See all the permanent and rotational modifiers.'
    )
    async def mods(self, ctx):
        mods = ModData.get()
        rotmods = ModData.get_rot()
        e = discord.Embed(title='Modifiers', colour=colours['hotpink'])
        e.add_field(
            name='Permanent', value=Utils.pretty_mods(mods), inline=False
        )
        e.add_field(name='Rotational', value=Utils.pretty_mods(rotmods))
        await ctx.send(embed=e)

    @commands.command(
        brief='Delete a permanent modifier.',
        description=(
            'Delete a permanent modifier (one that stays the same the whole '
            'game) by number (see `{{pre}}mods`). Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def delmod(self, ctx, num: int):
        s, m = ModData.rem(num)
        if s:
            ModData.save()
            return await ctx.send(f'Modifier `{m}` deleted.')
        await ctx.send(f'Error: {m}.')

    @commands.command(
        brief='Delete a rotational modifier.',
        description=(
            'Delete a rotational modifier (one that changes every round) by '
            'number (see `{{pre}}mods`). Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def delrotmod(self, ctx, num: int):
        s, m = ModData.rem_rot(num)
        if s:
            ModData.save()
            return await ctx.send(f'Modifier `{m}` deleted.')
        await ctx.send(f'Error: {m}.')

    @commands.command(
        brief='Clear all the modifiers.',
        description=(
            'Delete every permanent and rotational modifier for this server. '
            'Requires the sultan role.'
        )
    )
    @Utils.mod_check()
    async def clearmods(self, ctx):
        await ctx.send(
            'Are you sure you want to delete *every* modifier? (`yes` to '
            'continue, anything else to cancel)'
        )

        def check(mes):
            return (mes.author == ctx.author) and (mes.channel == ctx.channel)
        mes = await bot.wait_for('message', check=check)
        if mes.content.lower() != 'yes':
            return await ctx.send('Whew! That was close...')
        ModData.clear()
        await ctx.send('All gone!')
        ModData.save()


# TODO: bug test
