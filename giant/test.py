from tests import models
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    models.test_users()
    models.test_games()
