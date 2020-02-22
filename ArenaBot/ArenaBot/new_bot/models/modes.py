import discord


class Mode:
    @classmethod
    def load(cls, data):
        return cls(**data)

    @classmethod
    def new(cls, **data):
        return cls(**data)

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
        self.win = win_pts
        self.loss = loss_pts

    @property
    def players(self):
        return self.teams * self.team_size

    def dump(self):
        return {
            'name': self.name,
            'teams': self.teams,
            'team_size': self.team_size,
            'mods': self.mods,
            'round_mods': self.round_mods,
            'win_pts': self.win,
            'loss_pts': self.loss,
        }

    def main_str(self):
        '''
        Main part of the descriptor. Looks like
        "2 modifiers per game, 5 player FFA".
        '''
        if self.team_size > 1:
            teams_part = (
                f'{Modes.nums[self.teams]} teams of '
                f'{Modes.nums[self.team_size]}'
            )
        elif self.teams > 4:
            teams_part = f'{Modes.nums[self.teams]} player FFA'
        else:
            teams_part = ('1v' * self.teams)[:-1]
        s = ''
        if self.mods - 1:
            s = 's'
        per = ('game', 'round')[self.round_mods]
        mods = Modes.nums[self.mods].title()
        win = Modes.nums[self.win]
        loss = Modes.nums[self.loss]
        return (
            f'{mods} modifier{s} per {per}, {teams_part}. Win: {win} points; '
            f'loose: {loss} points.'
        )

    def __str__(self):
        '''
        Format for game info.
        '''
        return '{} ({})'.format(self.name, self.main_str())


class Modes:
    nums = {
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
    @classmethod
    def load(cls, bot):
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

    @classmethod
    def all(cls):
        e = discord.Embed(
            title='Game modes',
            description='​',     # ZWSP
            color=0x00ffff
        )
        for mode in cls.modes:
            e.add_field(name=mode.name, value=mode.main_str())
        return e

    @classmethod
    def get_mode(cls, arg):
        '''Convert a game mode as command parameter.
        '''
        for i in cls.modes:
            if i.name == arg.lower():
                return i

    @classmethod
    def save(cls):
        pass

