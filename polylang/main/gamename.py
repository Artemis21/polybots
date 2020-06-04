"""Utility for user renaming of channels, including game name validation."""
import random


language = [
    'po', 'ly', 'lu', 'mi', 'lo', 'da', 'bi', 'oo', 'sa', 'ko', 'me', 'da',
    'to', 'pi', 'as', 'an', 'ki'
]
templates = [
    '[action] of [place]', '[nature] of [place]', '[place]ian [action]',
    '[place]ian [nature]', '[super] [action]', 'The [nature] of [action]',
    'The [super] [nature]', '[nature] & [action]'
]
actions_crazy = [
    'Clowns', 'Bongo', 'Duh!', 'Squeal', 'Squirrel', 'Confusion', 'Gruff',
    'Moan', 'Chickens', 'Spunge', 'Gnomes', 'Bell boys', 'Gurkins',
    'Commotion', 'LOL', 'Shenanigans', 'Hullabaloo', 'Papercuts', 'Eggs',
    'Mooni', 'Gaami'
]
actions = [
    'War', 'Spirit', 'Faith', 'Glory', 'Blood', 'Empires', 'Songs', 'Dawn',
    'Prophecy', 'Gold', 'Fire', 'Swords', 'Queens', 'Knights', 'Kings',
    'Tribes', 'Tales', 'Quests', 'Change', 'Games', 'Throne', 'Conquest',
    'Struggle', 'Victory', 'Battles', 'Legends', 'Heroes', 'Storms', 'Clouds',
    'Gods', 'Love', 'Lords', 'Lights', 'Wrath', 'Destruction', 'Whales',
    'Ruins', 'Monuments', 'Wonder'
]
superlatives_crazy = [
    'Gruffy', 'Slimy', 'Silly', 'Unwilling', 'Stumbling', 'Drunken', 'Merry',
    'Mediocre', 'Normal', 'Stupid', 'Moody', 'Tipsy', 'Trifling', 'Rancid',
    'Numb'
]
superlatives = [
    'Epic', 'Endless', 'Glorious', 'Brave', 'Misty', 'Mysterious', 'Lost',
    'Cold', 'Amazing', 'Doomed', 'Glowing', 'Glimmering', 'Magical', 'Living',
    'Thriving', 'Bold', 'Dark', 'Bright', 'Majestic', 'Shimmering', 'Lucky',
    'Great', 'Everlasting', 'Eternal', 'Superb', 'Frozen'
]
natures_crazy = [
    'Custard', 'Goon', 'Cat', 'Spagetti', 'Fish', 'Fame', 'Popcorn', 'Dessert',
    'Space'
]
natures = [
    'Hills', 'Fields', 'Lands', 'Forest', 'Ocean', 'Fruit', 'Mountain', 'Lake',
    'Paradise', 'Jungle', 'Desert', 'River', 'Sea', 'Shores', 'Valley',
    'Garden', 'Moon', 'Star', 'Winter', 'Spring', 'Summer', 'Autumn',
    'Divide', 'Square', 'Glacier', 'Ice'
]


def game(crazy=False):
    name = random.choice(templates)
    if crazy and random.randrange(2):
        action = random.choice(actions_crazy)
    else:
        action = random.choice(actions)
    place = word()
    if crazy and random.randrange(2):
        superl = random.choice(superlatives_crazy)
    else:
        superl = random.choice(superlatives)
    if crazy and random.randrange(2):
        nature = random.choice(natures_crazy)
    else:
        nature = random.choice(natures)
    name = name.replace('[action]', action).replace('[place]', place)
    name = name.replace('[super]', superl).replace('[nature]', nature)
    return name


def word():
    word = ''
    while len(word) < random.randrange(3, 6):
        word += random.choice(language)
    return word[0].upper() + word[1:]
