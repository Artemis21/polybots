import json
import random
import string
import discord


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
        return cls(name, players, lives, tid, extra, games, wins)

    @classmethod
    def new(cls, name, players):
        random.seed(name)
        lets = string.ascii_uppercase + string.digits
        team_id = ''.join(random.choices(lets, k=5))
        return cls(name, players, 3, team_id, '', 0, 0)

    def __init__(self, name, players, lives, team_id, extra, games, wins):
        self.name = name
        self.players = players
        self.lives = lives
        self.team_id = team_id
        self.extra = extra
        self.games = games
        self.wins = wins

    def dump(self):
        return {
            'name': self.name,
            'players': [i.id for i in self.players],
            'lives': self.lives,
            'extra': self.extra,
            'games': self.games,
            'wins': self.wins,
        }

    def loose(self):
        self.lives -= 1
        return self.lives == 0

    def win(self):
        self.wins += 1

    def display(self):
        e = discord.Embed(title=self.name)
        e.add_field(
            name='Members', value='\n'.join(i.mention for i in self.players)
        )
        e.add_field(name='Team ID', value=self.team_id)
        e.add_field(name='Lives Remaining', value=self.lives)
        e.add_field(name='ELO', value=self.extra or '<not given>')
        e.add_field(name='Games', value=f'{self.games} ({self.wins} won)')
        return e


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
    def add_team(cls, name, members, bot):
        if cls.stage == 'not started':
            return False, 'Signups aren\'t open yet!'
        if cls.stage == 'in progress':
            return False, 'Signups have closed :('
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        new = Team.new(name, members)
        cls.teams[new.team_id] = new
        return True, 'Team created!'

    @classmethod
    def remove_team(cls, team_id):
        if team_id in cls.teams:
            del cls.teams[team_id]
            return True, 'Team removed...'
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def convert(cls, raw_arg):
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
    def conclude(cls, looser, winner):
        if cls.stage == 'not started':
            return False, 'The game hasn\'t even started yet!'
        if cls.stage == 'signup':
            return False, 'Game still on signups.'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        if (looser in cls.teams) and (winner in cls.teams):
            looser = cls.teams[looser]
            winner = cls.teams[winner]
            mess = [
                f'\nTeam {looser.name} is on {looser.lives} life/lives.',
                f'Team {winner.name} has been awarded a win!.'
            ]
            dead = team.loose()
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
        if cls.stage == 'not started':
            return False, 'The game hasn\'t even started yet!'
        if cls.stage == 'ended':
            return False, 'The tourney is over for this year!'
        if team_id in cls.teams:
            try:
                extra = int(extra)
            except ValueError:
                return False, 'That\'s not a valid number!'
            if extra > 2550:
                return False, 'Combined local ELO may not be more than 2550!'
            team = cls.teams[team_id]
            team.extra = extra
            return (
                True,
                f'Combined local ELO for team {team.name} set to `{extra}`.'
            )
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
        if team_id in cls.teams:
            return True, cls.teams[team_id].display()
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def open_game(cls, team_id, team_id2):
        if team_id in cls.teams:
            return True, cls.teams[team_id].display()
        else:
            return False, 'That team doesn\'t exist :/'

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
            json.dump(data, f)
