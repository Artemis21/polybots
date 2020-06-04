from .generic import DivisionSpecificModel


class User(DivisionSpecificModel):
    @classmethod
    def create(
            cls, id: int, division: str, name: str = 'Not set',
            code: str = 'Not set', league: int = 4, points: int = 0
            ):
        data = {
            'league': league,
            'division': division,
            'points': points,
            'name': name,
            'code': code,
        }
        return super().create(data, id)
