import models
from logging import log, INFO, WARNING


TEST_USER = {
    'id': 123456789012,
    'name': 'Artemis',
    'code': 'wg34g3b35n35n45nEGG',
}
TEST_USER_2 = {
    'id': 987654321098,
    'name': 'Apollo',
    'code': 'oNG90nonnaf090aFF0j',
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



if __name__ == '__main__':
    test_users()
    test_games()
