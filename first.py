#!/usr/bin/env python

import random, sys

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


def initial_matchups(num_teams):
    print('{} teams.'.format(num_teams))
    if (num_teams % 2 == 1):
        num_teams = num_teams + 1
        print('We\'re going to pretend there are {} teams, OK?'.format(num_teams))

    first, second = pick_odd_numbers(num_teams)
    for firstboy in range(1, num_teams, 2):
        firstgirl = 1 + ((firstboy + first - 1) % num_teams)
        secondboy = 1 + ((firstboy + second - 1) % num_teams)
        secondgirl = 1 + ((firstboy + first + second - 1) % num_teams)
        print('M{}F{} M{}F{}'.format(firstboy, firstgirl, secondboy, secondgirl))
    
            

if len(sys.argv) == 2:
    initial_matchups(int(sys.argv[1]))
else:
    print('Not implemented yet!')
