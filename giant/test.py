from tests import models
from logging import basicConfig, log, INFO, WARNING


def test():
    log(INFO, 'Starting tests')
    models.test()


if __name__ == '__main__':
    basicConfig(level=WARNING)
    test()
    print('Tests complete')
