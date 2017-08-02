#!/usr/bin/env python

import fileinput, random, sys

players = list()

MAX_TRIES = 1000
def acceptable(first, second, num_teams):
    if (first == second):
        return False
    if (first % 2 == 0):
        return False
    if (second % 2 == 0):
        return False
    if ((first + second) % num_teams == 0):
        return False
    return True

def pick_odd_numbers(num_teams):
    num_tries = 0
    while True and num_tries < MAX_TRIES:
        first = random.randrange(1,num_teams,2)
        second = random.randrange(1,num_teams,2)
        if acceptable(first, second, num_teams):
            break
        num_tries = num_tries + 1
    if num_tries == MAX_TRIES:
        print('Couldnt find good random odd numbers!  I quit.')
        sys.exit()
    else:
        print('Randomly chosen odd numbers are {} and {}.'.format(first, second))
        
    return first, second

def boy_name(number):
    global players
    try:
        return players[(number * 2) - 2]
    except Exception:
        return "BYE"

def girl_name(number):
    global players
    try:
        return players[(number * 2) - 1]
    except Exception:
        return "BYE"

def initial_matchups(players):
    if len(players) % 4 != 0:
        print('Need an even number of teams!  Currently there are {} players, no good.'.format(len(players)))
        sys.exit(0)

    num_teams = len(players) / 2
    print('{} teams.'.format(num_teams))
    if (num_teams % 2 == 1):
        num_teams = num_teams + 1
        print('We\'re going to pretend there are {} teams, OK?'.format(num_teams))

    lineup = list()
        
    first, second = pick_odd_numbers(num_teams)
    for firstboy in range(1, num_teams, 2):
        firstgirl = 1 + ((firstboy + first - 1) % num_teams)
        secondboy = 1 + ((firstboy + second - 1) % num_teams)
        secondgirl = 1 + ((firstboy + first + second - 1) % num_teams)
        lineup.append((firstboy, firstgirl, secondboy, secondgirl))

    for fb,fg,sb,sg in lineup:
        print('{} / {} (M{}F{}) vs {} / {} (M{}F{})'.format(boy_name(fb), girl_name(fg), fb, fg, boy_name(sb), girl_name(sg), sb, sg))


def read_roster():
    for line in fileinput.input():
        players.append(line.strip())
    return players


players = read_roster()

initial_matchups(players)

