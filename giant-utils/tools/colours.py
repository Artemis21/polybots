import random


ERROR = 0xFF2A2A
SUCCESS = 0x00F42F
HELP = 0x2AAF21
THEME_COLS = (
    0xFF7733,
    0xF3CA40,
    0x006E90,
    0xD81159,
)


def theme():
    return random.choice(THEME_COLS)
