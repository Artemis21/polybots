import models
from logging import basicConfig, log, DEBUG, INFO, WARNING


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
    log(INFO, 'Starting user model tests')
    log(DEBUG, 'Creating user')
    user = models.User.create(**TEST_USER, division='B')
    log(DEBUG, 'Giving user points')
    user.points += 10
    log(DEBUG, 'Clearing user cache')
    models.User.clear_cache()
    log(DEBUG, 'Getting user')
    user = models.User.load(user.id)
    log(DEBUG, 'Checking points')
    if user.points != 10:
        log(
            WARNING,
            'User points did not update correctly, should be 10 not '
            + '{}.'.format(user['points'])
        )
    log(DEBUG, 'Creating a second user')
    models.User.create(**TEST_USER_2, division='C')
    log(DEBUG, 'Fetching all users')
    if len(models.User.all()) != 2:
        log(
            WARNING,
            'Incorrect number of users, should be 2 not '
            + f'{len(models.User.all())}.'
        )
    log(DEBUG, 'Deleting first user')
    user.delete()
    log(DEBUG, 'Deleting all users')
    models.User.delete_all()
    if len(models.User.all()):
        log(
            WARNING,
            'Incorrect number of users, should be 0 not '
            + f'{len(models.User.all())}.'
        )


def test_games():
    log(INFO, 'Starting game model tests')
    log(DEBUG, 'Creating a game')
    game = models.Game.create(**TEST_GAME)
    log(DEBUG, 'Setting the name')
    game.name = 'Popcorn and Moans'
    log(DEBUG, 'Registering a kill')
    game.kills[TEST_USER_2['id']] = TEST_KILL
    log(DEBUG, 'Checking name')
    if game.name != 'Popcorn and Moans':
        log(
            WARNING,
            'Game name should be "Popcorn and Moans", not "{}".'.format(
                game.name
            )
        )
    log(DEBUG, 'Clearing the cache')
    models.Game.clear_cache()
    log(DEBUG, 'Getting the game')
    game = models.Game.load(game.id)
    log(DEBUG, 'Checking kills')
    if dict(game.kills) != {TEST_USER_2['id']: TEST_KILL}:
        log(
            WARNING,
            'Kills should be {}, not {}.'.format(
                {TEST_USER_2['id']: TEST_KILL}, game.kills
            )
        )
    log(DEBUG, 'Creating a second game')
    models.Game.create(**TEST_GAME_2)
    log(DEBUG, 'Finding games by division')
    games = models.Game.all_in_division(4, 'B', 2)
    if len(games) != 2:
        log(WARNING, 'There should be 2 games, not {}.'.format(len(games)))
    log(DEBUG, 'Deleting all games by division')
    models.Game.delete_all({'division': 'B'})
    log(DEBUG, 'Checking number of games')
    if models.Game.all():
        log(
            WARNING,
            "There shouldn't be any games left but there are {}.".format(
                len(models.Game.all())
            )
        )


def test_settings():
    log(INFO, 'Starting settings model tests')
    log(DEBUG, 'Adding an admin role')
    models.Settings.admin_roles.append(100)
    log(DEBUG, 'Setting the season')
    models.Settings.season = 10
    log(DEBUG, 'Clearing admin users')
    models.Settings.admin_users.clear()
    log(DEBUG, 'Reloading settings')
    models.Settings.load()
    log(DEBUG, 'Checking admin roles')
    if list(models.Settings.admin_roles) != [100]:
        log(
            WARNING,
            'Admin roles should be [100] not {}.'.format(
                models.Settings.admin_roles
            )
        )
    log(DEBUG, 'Checking season')
    if models.Settings.season != 10:
        log(
            WARNING,
            'Season should be 10 not {}.'.format(models.Settings.season)
        )
    log(DEBUG, 'Checking admin users')
    if models.Settings.admin_users:
        log(
            WARNING,
            'There should be no admin users, not {}.'.format(
                models.Settings.admin_users
            )
        )
    log(DEBUG, 'Resetting defaults')
    models.Settings.reset()
    if 100 in models.Settings.admin_roles:
        log(
            WARNING,
            '100 should not be an admin role.'
        )
        

def test():
    log(INFO, 'Starting model tests')
    test_users()
    test_games()
    test_settings()


if __name__ == '__main__':
    basicConfig(level=WARNING)
    test()
