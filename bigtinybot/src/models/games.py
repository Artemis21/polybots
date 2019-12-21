class Game:
    @classmethod
    def load(cls, data):
        home = data['home']
        away = data['away']
        return cls(home, away)

    @classmethod
    def new(cls, home, away):
        return cls(home, away)

    def __init__(self, home, away):
        self.home = home
        self.away = away

    def dump(self):
        return {
            'home': self.home,
            'away': self.away
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
