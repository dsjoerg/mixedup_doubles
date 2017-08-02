#!/usr/bin/env python

import fileinput, random, re, sys

players = list()  # Player names: 0:M1, 1:F1, 2:M2, 3:F2, etc
winners = list()  # Index number of players still in winners bracket, indexes from players list.
losers = list()   # Index number of players still in losers bracket, indexes from players list.
games = list()    # Quads of games that have been played.  Each quad has the four indexes of the players who played.

MAX_TRIES = 1000

def name(index):
    global players
    try:
        return players[index]
    except Exception:
        return "BYE"

def number(index):
    if index % 2 == 0:
        return (1 + index/2)
    else:
        return ((index+1)/2)
    
def dfi(index):
    '''For example 5 returns F3'''
    if index % 2 == 0:
        return 'M{}'.format(number(index))
    else:
        return 'F{}'.format(number(index))
    
def boy_index(number):
    '''For example boy_index(2) returns 2 because
    M2 is the third element in the zero-indexed players list'''
    return (number * 2) - 2

def girl_index(number):
    '''For example girl_index(3) returns 5 because
    F3 is the sixth element in the zero-indexed players list'''
    return (number * 2) - 1


def read_roster():
    for line in fileinput.input(sys.argv[1]):
        players.append(line.strip())
    return players

def read_result_line(line):
    '''Read and validate this line of results.
    Make sure there are four numbers and all numbers refer to players.
    '''
    m = re.search('M([0-9]+)F([0-9]+) M([0-9]+)F([0-9]+)', line)
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))

def complain(complaint):
    print(complaint)
    sys.exit(0)

def expect_equal(a, b, complaint_template):
    if a != b:
        complain(complaint_template.format(a,b))


def read_results():
    '''Read and validate all results.
    Everyone plays once and only once.
    '''
    for line in fileinput.input(sys.argv[2]):
        boywin, girlwin, boylose, girllose = read_result_line(line)
        winners.append(boy_index(boywin))
        winners.append(girl_index(girlwin))
        losers.append(boy_index(boylose))
        losers.append(girl_index(girllose))
        games.append((boy_index(boywin), girl_index(girlwin), boy_index(boylose), girl_index(girllose)))

    expect_equal(len(players)/4, len(games), 'Expected {} games but only got results for {}.')
    expect_equal(len(players)/2, len(winners), 'Expected {} winners but only have {}.')
    expect_equal(len(players)/2, len(losers), 'Expected {} losers but only have {}.')
    expect_equal(0, len(set(winners) & set(losers)), 'Expected {} players in both winners and losers, but have {}.')

def show_round_one_results():
    print 'ROUND ONE RESULTS:'
    for game in games:
        print('{} / {} ({}{}) defeated {} / {} ({}{})'.format(name(game[0]), name(game[1]), dfi(game[0]), dfi(game[1]), name(game[2]), name(game[3]), dfi(game[2]), dfi(game[3])))

def played_before(a, b):
    for game in games:
        gameplayers = set(list(game))
        if ((a in gameplayers) and (b in gameplayers)):
            return True
    return False
        
def pair_ok(boy, girl):
    if number(boy) == number(girl):
        return False   # dont play with spouse
    if played_before(boy, girl):
        return False   # dont play with or against anyone youve played with before
    return True

def opponent_ok(a, b):
    if number(a) == number(b):
        return False   # dont play against spouse
    if played_before(a, b):
        return False   # dont play with or against anyone youve played with before
    return True

def show_pairings(pairings):
    for fb,fg,sb,sg in pairings:
        print('{} / {} ({}{}) vs {} / {} ({}{})'.format(name(fb), name(fg), dfi(fb), dfi(fg), name(sb), name(sg), dfi(sb), dfi(sg)))

def pair_from_pool(pool, pool_name):
    print('')
    numstarts = 0
    lineup = list()
    while numstarts < MAX_TRIES:
        numstarts = numstarts + 1
        working_pool = list(pool)
        
        lineup = list()
        numtries = 0
        while len(working_pool) > 0 and numtries < MAX_TRIES:
            numtries = numtries + 1

            boy_pool = [x for x in working_pool if x % 2 == 0]
            girl_pool = [x for x in working_pool if x % 2 == 1]

            boy_player = random.choice(boy_pool)
            eligible_girls = [x for x in girl_pool if pair_ok(boy_player, x)]
            if len(eligible_girls) == 0:
#                print('ACK', len(lineup), lineup)
                continue
            girl_player = random.choice(eligible_girls)

            eligible_boy_opponents = [x for x in boy_pool if x != boy_player and opponent_ok(boy_player, x) and opponent_ok(girl_player, x)]
            if len(eligible_boy_opponents) == 0:
#                print('NO WAY', len(lineup), lineup)
                continue
            boy_opponent = random.choice(eligible_boy_opponents)
            eligible_girl_opponents = [x for x in girl_pool if x != girl_player and opponent_ok(boy_player, x) and opponent_ok(girl_player, x) and pair_ok(boy_opponent, x)]
            if len(eligible_girl_opponents) == 0:
#                print('UGGGGHHHH', len(lineup), lineup)
                continue
            girl_opponent = random.choice(eligible_girl_opponents)

            lineup.append((boy_player, girl_player, boy_opponent, girl_opponent))
            working_pool.remove(boy_player)
            working_pool.remove(girl_player)
            working_pool.remove(boy_opponent)
            working_pool.remove(girl_opponent)

        if len(working_pool) == 0:
            # we found pairings that use everyone
            break
        else:
            # we tried but got stuck
            print('I got stuck trying to make a {} pairing:'.format(pool_name))
            show_pairings(lineup)
            print('Unpairable: {}'.format(', '.join(['{} ({})'.format(name(x), dfi(x))  for x in working_pool])))
            print('')


    if numstarts < MAX_TRIES:
        print('{} PAIRINGS:'.format(pool_name))
        show_pairings(lineup)
        return lineup
    else:
        print('Couldnt find anything')
        return None

    

players = read_roster()
read_results()
show_round_one_results()
pair_from_pool(winners, 'WINNERS')
pair_from_pool(losers, 'LOSERS')

