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
        return cls(name, players, lives, tid)

    @classmethod
    def new(cls, name, players):
        random.seed(name)
        lets = string.ascii_uppercase + string.digits
        team_id = ''.join(random.choices(lets, k=5))
        return cls(name, players, 3, team_id)

    def __init__(self, name, players, lives, team_id):
        self.name = name
        self.players = players
        self.lives = lives
        self.team_id = team_id

    def dump(self):
        return {
            'name': self.name,
            'players': [i.id for i in self.players],
            'lives': self.lives
        }

    def loose(self):
        self.lives -= 1
        return self.lives == 0

    def display(self):
        e = discord.Embed(title=self.name)
        e.add_field(
            name='Members', value='\n'.join(i.mention for i in self.players)
        )
        e.add_field(name='Team ID', value=self.team_id)
        e.add_field(name='Lives Remaining', value=self.lives)
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
        self.teams = {}
        for i in raw['teams']:
            self.teams[i] = Team.load(raw[i]['teams'], i, bot)
        self.stage = raw['stage']    # not started/signup/in progress/ended
        self.winner = self.teams.get(raw['winner'], None)

    @classmethod
    def add_team(cls, name, members, bot):
        if self.stage == 'not started':
            return False, 'Signups aren\'t open yet!'
        if self.stage == 'in progress':
            return False, 'Signups have closed :('
        if self.stage == 'ended':
            return False, 'The tourney is over for this year!'
        new = Team.new(name, members)
        self.teams[new.team_id] = new
        return True, 'Team created!'

    @classmethod
    def remove_team(cls, team_id):
        if team_id in self.teams:
            del self.teams[team_id]
            return True, 'Team removed...'
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def convert(cls, raw_arg):
        if raw_arg in self.teams:
            return self.teams[raw_arg]
        raise ValueError('Team doesn\'t exist')

    @classmethod
    def find_by_member(cls, user):
        for i in self.teams:
            if user in i.players:
                return i
        return None

    @classmethod
    def give_loss(cls, team_id):
        if team_id in self.teams:
            dead = self.teams[team_id].loose()
            if len(self.teams) == 1:
                self.winner = self.teams[[*self.teams.keys()][0]]
                self.stage = 'ended'
                return (
                    True,
                    f'The tourney is over with {self.winner.name} victorious!'
                )
            if dead:
                return True, f'Team {team.name} eliminated!'
            else:
                return True, f'Team {team.name} is on {team.lives} life/lives.'
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def details(cls):
        e = discord.Embed(title='TinyTourny')
        e.add_field(name='Status', value=self.stage.title())
        e.add_field(name='Teams', value=len(self.teams))
        if self.winner:
            e.add_field(name='Winner', value=self.winner.name)
        return e

    @classmethod
    def team_details(cls, team_id):
        if team_id in self.teams:
            return True, self.teams[team_id].display()
        else:
            return False, 'That team doesn\'t exist :/'

    @classmethod
    def open(cls):
        if self.stage == 'signup':
            return False, 'Signups already opened!'
        if self.stage == 'in progress':
            return False, 'Game already in progress...'
        if self.stage == 'ended':
            return False, 'The tourney is over for this year!'
        self.stage = 'signup'
        return True, 'Signups opened!'

    @classmethod
    def start(cls):
        if self.stage == 'not started':
            return False, 'Signups haven\'t even opened yet!'
        if self.stage == 'in progress':
            return False, 'Game already in progress...'
        if self.stage == 'ended':
            return False, 'The tourney is over for this year!'
        self.stage = 'in progress'
        return True, 'Tourney begun!'

    @classmethod
    def reset(cls):
        self.teams = {}
        self.stage = 'not started'
        self.winner = None

    @classmethod
    def save(cls):
        teams = {}
        for i in self.teams:
            teams[i] = self.teams[i].dump()
        data = {
            'stage': self.stage,
            'teams': teams,
            'winner': getattr(self.winner, 'team_id', self.winner),
        }
        with open('data/teams.json') as f:
            json.dump(f, data)
