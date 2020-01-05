import json
import random
import string
import discord


def get_id(name):
    random.seed(name)
    lets = string.ascii_uppercase + string.digits
    team_id = ''.join(random.choices(lets, k=5))
    return team_id


class Team:
    @classmethod
    def load(cls, data, tid, bot):
        name = data['name']
        players = []
        for pid in data['players']:
            players.append(bot.get_user(pid))
        lives = data['lives']
        extra = data['extra']
        games = data['games']
        wins = data['wins']
        hosts = data['hosts']
        return cls(name, players, lives, tid, extra, games, wins, hosts)

    @classmethod
    def new(cls, name, players):
        team_id = get_id(name)
        return cls(name, players, 3, team_id, '', [], 0, 0)

    def __init__(
            self, name, players, lives, team_id, extra, games, wins, hosts
        ):
        self.name = name
        self.players = players
        self.lives = lives
        self.team_id = team_id
        self.extra = extra
        self.games = games
        self.wins = wins
        self.hosts = hosts

    def dump(self):
        return {
            'name': self.name,
            'players': [i.id for i in self.players],
            'lives': self.lives,
            'extra': self.extra,
            'games': self.games,
            'wins': self.wins,
            'hosts': self.hosts,
        }

    def loose(self):
        self.lives -= 1
        return self.lives == 0

    def win(self):
        self.wins += 1

    def play(self, game):
        self.games.append(game)

    def set_players(self, player1, player2):
        self.players = [player1, player2]

    def display(self):
        e = discord.Embed(title=self.name)
        e.add_field(
            name='Members', value='\n'.join(i.mention for i in self.players)
        )
        e.add_field(name='Team ID', value=self.team_id)
        e.add_field(name='Lives Remaining', value=self.lives)
        e.add_field(name='ELO', value=self.extra or '<not given>')
        e.add_field(
            name='Games',
            value=f'{len(self.games)} ({self.wins} won, {self.hosts} hosted)'
        )
        e.add_field(
            name='Playing Now',
            value=', '.join(self.playing) or 'no-one'
        )
        return e

    @property
    def playing(self):
        playing = []
        for i in self.games:
            if i['home'] == self.team_id:
                playing.append(i['away'])
            else:
                playing.append(i['home'])
        return playing

    def __str__(self):
        mentions = ', '.join((i.mention for i in self.players))
        return f'**{self.name}**, ID: `{self.team_id}` ({mentions})'


class Teams:
    @classmethod
    def load(cls, bot):
        try:
            with open('data/teams.json') as f:
                raw = json.load(f)
        except FileNotFoundError:
            raw = {}
        if 'teams' not in raw:
            raw['teams'] = {}
        if 'stage' not in raw:
            raw['stage'] = 'not started'
        if 'winner' not in raw:
            raw['winner'] = None
        cls.teams = {}
        for i in raw['teams']:
            cls.teams[i] = Team.load(raw['teams'][i], i, bot)
        cls.stage = raw['stage']    # not started/signup/in progress/ended
        cls.winner = cls.teams.get(raw['winner'], None)

    @classmethod
    def add_team(cls, name, members):
        if cls.stage == 'not started':
            return False, 'Signups aren\'t open yet!'
        if cls.stage == 'in progress':
            return False, 'Signups have closed :('
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        name = name.replace('\n', '').strip()[:20]
        if members[0] == members[1]:
            return False, 'You can\'t have a team by yourself!'
        for i in members:
            if cls.find_by_member(i):
                return False, f'{i} is already in a team.'
        tid = get_id(name)
        if tid in cls.teams:
            return False, 'That name is already taken.'
        new = Team.new(name, members)
        cls.teams[new.team_id] = new
        return True, 'Team created!'

    @classmethod
    def remove_team(cls, team_id):
        if team_id.upper() in cls.teams:
            del cls.teams[team_id.upper()]
            return True, 'Team removed...'
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def convert(cls, raw_arg):
        raw_arg = raw_arg.upper()
        if raw_arg in cls.teams:
            return cls.teams[raw_arg]
        raise ValueError('Team doesn\'t exist')

    @classmethod
    def find_by_member(cls, user):
        for i in cls.teams:
            if user in cls.teams[i].players:
                return cls.teams[i]
        return None

    @classmethod
    def find_by_id(cls, team_id):
        return cls.teams.get(team_id.upper(), None)

    @classmethod
    def conclude(cls, looser, winner):
        looser, winner = looser.upper(), winner.upper()
        if cls.stage == 'not started':
            return False, 'The game hasn\'t even started yet!'
        if cls.stage == 'signup':
            return False, 'Game still on signups.'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        if (looser in cls.teams) and (winner in cls.teams):
            looser = cls.teams[looser]
            winner = cls.teams[winner]
            if looser.team_id not in winner.playing:
                return False, f'{looser.name} isn\'t playing {winner.name}.'
            mess = [
                f'\nTeam {looser.name} is on {looser.lives-1} life/lives.',
                f'Team {winner.name} has been awarded a win!'
            ]
            dead = looser.loose()
            winner.win()
            if dead:
                del cls.teams[team_id]
                mess.append(f'Team {team.name} eliminated!')
            if len(cls.teams) == 1:
                cls.winner = cls.teams[[*cls.teams.keys()][0]]
                cls.stage = 'ended'
                mess.append(
                    f'The tourney is over with {cls.winner.name} victorious!'
                )
            return True, '\n'.join(mess)
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def set_extra(cls, team_id, extra):
        team_id = team_id.upper()
        if cls.stage == 'not started':
            return False, 'The game hasn\'t even started yet!'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        if team_id in cls.teams:
            try:
                extra = int(extra)
            except ValueError:
                return False, 'That\'s not a valid number!'
            if extra > 2650:
                return False, 'Combined global ELO may not be more than 2650!'
            team = cls.teams[team_id]
            team.extra = extra
            return (
                True,
                f'Combined global ELO for team {team.name} set to `{extra}`.'
            )
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def set_players(cls, team_id, player1, player2):
        team_id = team_id.upper()
        if cls.stage == 'not started':
            return False, 'The game hasn\'t even started yet!'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        if team_id in cls.teams:
            team = cls.teams[team_id]
            if player1 == player2:
                return False, 'You can\'t have a team by yourself!'
            for i in (player1, player2):
                if cls.find_by_member(i) not in (None, team):
                    return False, f'{i} is already in a team.'
            team.set_players(player1, player2)
            return (
                True,
                f'Team {team.name}\'s players are now {player1} and {player2}.'
            )
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def rename(cls, team_id, name):
        team_id = team_id.upper()
        if cls.stage == 'not started':
            return False, 'The game hasn\'t even started yet!'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        if team_id in cls.teams:
            name = name.replace('\n', '').strip()[:20]
            tid = get_id(name)
            team = cls.teams[team_id]
            if tid in cls.teams and cls.teams[tid] != team:
                return False, 'That name is already taken.'
            # FIXME: the id doesn't update so the dupe name checking will break
            team.name = name
            return True, 'Name updated.'
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def details(cls):
        e = discord.Embed(title='TinyTourny')
        e.add_field(name='Status', value=cls.stage.title())
        e.add_field(name='Teams', value=len(cls.teams))
        if cls.winner:
            e.add_field(name='Winner', value=cls.winner.name)
        return e

    @classmethod
    def team_details(cls, team_id):
        team = cls.find_by_id(team_id)
        if team:
            return True, team.display()
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def open_game(cls, team_id, team_id2):
        home = cls.find_by_id(team_id)
        away = cls.find_by_id(team_id2)
        if home and away:
            game = {
                'home': home.team_id,
                'away': away.team_id
            }
            home.play(game)
            away.play(game)
            home.hosts += 1
            return (
                True,
                f'Opened game between {home.name} (host) and {away.name}.'
            )
        else:
            return False, 'At least one of those teams doesn\'t exist :/'

    @classmethod
    def open(cls):
        if cls.stage == 'signup':
            return False, 'Signups already opened!'
        if cls.stage == 'in progress':
            return False, 'Game already in progress...'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        cls.stage = 'signup'
        return True, 'Signups opened!'

    @classmethod
    def start(cls):
        if cls.stage == 'not started':
            return False, 'Signups haven\'t even opened yet!'
        if cls.stage == 'in progress':
            return False, 'Game already in progress...'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        cls.stage = 'in progress'
        return True, 'Tourney begun!'

    @classmethod
    def reset(cls):
        cls.teams = {}
        cls.stage = 'not started'
        cls.winner = None

    @classmethod
    def save(cls):
        teams = {}
        for i in cls.teams:
            teams[i] = cls.teams[i].dump()
        data = {
            'stage': cls.stage,
            'teams': teams,
            'winner': getattr(cls.winner, 'team_id', cls.winner),
        }
        with open('data/teams.json', 'w') as f:
            json.dump(data, f, indent=4)
