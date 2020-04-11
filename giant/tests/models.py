import models
from logging import basicConfig, log, INFO, WARNING


TEST_USER = {
    'id': 123456789012,
    'name': 'Artemis',
    'code': 'wg34g3b35n35n45nEGG',
}
TEST_USER_2 = {
    'id': 987654321098,
    'name': 'Apollo',
    'code': 'oNG90noN090aFF0j',
}
TEST_GAME = {
    'host': TEST_USER['id'],
    'division': 'B',
    'league': 4,
    'season': 2
}
TEST_GAME_2 = {
    'host': TEST_USER_2['id'],
    'division': 'B',
    'league': 4,
    'season': 2
}
TEST_KILL = {
    'code': 'C',
    'killer': TEST_USER['id'],
    'turn': 10
}


def test_users():
    log(INFO, 'Setting up database...')
    models.setup()
    log(INFO, 'Creating user...')
    user = models.User.create(**TEST_USER, division='B')
    log(INFO, 'Giving user points...')
    user.points += 10
    log(INFO, 'Clearing user cache...')
    models.User.clear_cache()
    log(INFO, 'Getting user...')
    user = models.User.load(user.id)
    log(INFO, 'Checking points...')
    if user.points != 10:
        log(
            WARNING,
            'User points did not update correctly, should be 10 not '
            + '{}.'.format(user['points'])
        )
    log(INFO, 'Creating a second user...')
    models.User.create(**TEST_USER_2, division='C')
    log(INFO, 'Fetching all users...')
    log(INFO, str(models.User.all()))
    if len(models.User.all()) != 2:
        log(
            WARNING,
            'Incorrect number of users, should be 2 not '
            + f'{len(models.User.all())}.'
        )
    log(INFO, 'Deleting first user...')
    user.delete()
    log(INFO, 'Deleting all users...')
    models.User.delete_all()
    if len(models.User.all()):
        log(
            WARNING,
            'Incorrect number of users, should be 0 not '
            + f'{len(models.User.all())}.'
        )


def test_games():
    log(INFO, 'Setting up database...')
    models.setup()
    log(INFO, 'Creating a game...')
    game = models.Game.create(**TEST_GAME)
    log(INFO, 'Setting the name...')
    game.name = 'Popcorn and Moans'
    log(INFO, 'Registering a kill...')
    game.kills[TEST_USER_2['id']] = TEST_KILL
    log(INFO, 'Checking name...')
    if game.name != 'Popcorn and Moans':
        log(
            WARNING,
            'Game name should be "Popcorn and Moans", not "{}".'.format(
                game.name
            )
        )
    log(INFO, 'Clearing the cache...')
    models.Game.clear_cache()
    log(INFO, 'Getting the game...')
    game = models.Game.load(game.id)
    log(INFO, 'Checking kills...')
    if dict(game.kills) != {TEST_USER_2['id']: TEST_KILL}:
        log(
            WARNING,
            'Kills should be {}, not {}.'.format(
                {TEST_USER_2['id']: TEST_KILL}, game.kills
            )
        )
    log(INFO, 'Creating a second game...')
    models.Game.create(**TEST_GAME_2)
    log(INFO, 'Finding games by division...')
    games = models.Game.all_in_division(4, 'B', 2)
    if len(games) != 2:
        log(WARNING, 'There should be 2 games, not {}.'.format(len(games)))
    log(INFO, 'Deleting all games by division...')
    models.Game.delete_all({'division': 'B'})
    log(INFO, 'Checking number of games...')
    if models.Game.all():
        log(
            WARNING,
            "There shouldn't be any games left but there are {}.".format(
                len(models.Game.all())
            )
        )


if __name__ == '__main__':
    basicConfig(level=WARNING)
    test_users()
    test_games()
