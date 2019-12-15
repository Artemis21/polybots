import random


def can_play(team):
    return (team.wins+3) - team.games > 0


def find_game(team, teams):
    if teams.stage == 'not started':
        return False, 'The game hasn\'t even started yet!'
    if teams.stage == 'signup':
        return False, 'Game still on signups.'
    if teams.stage == 'ended':
        return False, 'The tourney is over for this year!'
    teams = teams.teams
    if not can_play(team):
        return False, 'You must win another game before you can play again!'
    pool = []
    for i in teams:
        i = teams[i]
        if i.wins == team.wins and can_play(i) and team != i:
            pool.append(i)
    if pool:
        opp = random.choice(pool)
        team.games += 1
        opp.games += 1
        return True, f'Game started between {team.name} and {opp.name}.'
    return False, 'No-one is ready to play with you just yet!'
