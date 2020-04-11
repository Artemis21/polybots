from .generic import DivisionSpecificModel,  ModelDict


class Game(DivisionSpecificModel):
    @classmethod
    def create(cls, host: int, division: str, league: int, season: int):
        data = {
            'host': host,
            'division': division,
            'league': league,
            'season': season,
            'name': None,
            'status': 'not started',
            'kills': ModelDict(None)
        }
        obj = super().create(data)
        obj.kills.game = obj
        return obj

    def __init__(self, id, data):
        data['kills'] = ModelDict(self, data['kills'])
        super().__init__(id, data)

    def __setattr__(self, name, value):
        if name == 'kills':
            value = {str(i): value[i] for i in value}
        super().__setattr__(name, value)
