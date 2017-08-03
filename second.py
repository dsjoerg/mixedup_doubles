#!/usr/bin/env python

import fileinput, random, re, sys

players = list()  # Player names: 0:M1, 1:F1, 2:M2, 3:F2, etc
winners = list()  # Index number of players still in winners bracket, indexes from players list.
losers = list()   # Index number of players still in losers bracket, indexes from players list.
games = list()    # Quads of games that have been played.  Each quad has the four indexes of the players who played.

MAX_TRIES = 1000
RELAX_THRESHOLD = 5

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

def expect(condition, message):
    if not condition:
        complain(message)

def read_results():
    '''Read and validate all results.
    Everyone plays once and only once.
    '''
    first_round_matches = len(players) / 4
    for line in fileinput.input(sys.argv[2]):
        boywin, girlwin, boylose, girllose = read_result_line(line)
        games.append((boy_index(boywin), girl_index(girlwin), boy_index(boylose), girl_index(girllose)))
        
        if fileinput.lineno() <= first_round_matches:
            # one of the first round matches.  put players in the winner and loser pools accordingly
            winners.append(boy_index(boywin))
            winners.append(girl_index(girlwin))
            losers.append(boy_index(boylose))
            losers.append(girl_index(girllose))

        if fileinput.lineno() == first_round_matches:
            # first round matches are done. lets check that things were done right
            expect_equal(len(players)/4, len(games), 'Expected {} games but got results for {}.')
            expect_equal(len(players)/2, len(winners), 'Expected {} winners but have {}.')
            expect_equal(len(players)/2, len(losers), 'Expected {} losers but have {}.')
            expect_equal(0, len(set(winners) & set(losers)), 'Expected {} players in both winners and losers, but have {}.')
                
        if fileinput.lineno() > first_round_matches:
            # a match was played after the first round.
            if boy_index(boywin) in winners:
                expected_pool = winners
            else:
                expected_pool = losers
                
            expect(girl_index(girlwin) in expected_pool, 'Expected {} in same pool as her teammate {}'.format(name(girl_index(girlwin)), name(boy_index(boywin))))
            expect(boy_index(boylose) in expected_pool, 'Expected {} in same pool as his opponent {}'.format(name(boy_index(boylose)), name(boy_index(boywin))))
            expect(girl_index(girllose) in expected_pool, 'Expected {} in same pool as her opponent {} was'.format(name(girl_index(girllose)), name(boy_index(boywin))))
            expected_pool.remove(boy_index(boylose))
            expected_pool.remove(girl_index(girllose))


def show_results():
    for game in games:
        print('{} / {} ({}{}) defeated {} / {} ({}{})'.format(name(game[0]), name(game[1]), dfi(game[0]), dfi(game[1]), name(game[2]), name(game[3]), dfi(game[2]), dfi(game[3])))

def played_before(a, b, try_number):
    if try_number < RELAX_THRESHOLD:
        # at first we look at all games
        for game in games:
            gameplayers = set(list(game))
            if ((a in gameplayers) and (b in gameplayers)):
                return True
    elif try_number < 2 * RELAX_THRESHOLD:
        # then we look only at the most recent game played by each person
        latest_game = [g for g in games if a in set(list(g))][-1]
        gameplayers = set(list(latest_game))
        if ((a in gameplayers) and (b in gameplayers)):
            return True
    else:
        # then we dont care about past games
        return False
        
def pair_ok(boy, girl, try_number):
    if number(boy) == number(girl) and try_number < 3 * RELAX_THRESHOLD:
        return False   # dont play with spouse
    if played_before(boy, girl, try_number):
        return False   # dont play with or against anyone youve played with before
    return True

def opponent_ok(a, b, try_number):
    if number(a) == number(b) and try_number < 3 * RELAX_THRESHOLD:
        return False   # dont play against spouse
    if played_before(a, b, try_number + 2):
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
            eligible_girls = [x for x in girl_pool if pair_ok(boy_player, x, numstarts)]
            if len(eligible_girls) == 0:
#                print('ACK', len(lineup), lineup)
                continue
            girl_player = random.choice(eligible_girls)

            eligible_boy_opponents = [x for x in boy_pool if x != boy_player and opponent_ok(boy_player, x, numstarts) and opponent_ok(girl_player, x, numstarts)]
            if len(eligible_boy_opponents) == 0:
#                print('NO WAY', len(lineup), lineup)
                continue
            boy_opponent = random.choice(eligible_boy_opponents)
            pool_girls = [x for x in girl_pool if x != girl_player]
            eligible_girl_opponents = [x for x in pool_girls if x != girl_player and opponent_ok(boy_player, x, numstarts) and opponent_ok(girl_player, x, numstarts) and pair_ok(boy_opponent, x, numstarts)]
            if len(eligible_girl_opponents) == 0:
#                print('UGGGGHHHH', len(lineup), lineup, dfi(boy_player), dfi(girl_player), dfi(boy_opponent), [dfi(x) for x in pool_girls])
                continue
            girl_opponent = random.choice(eligible_girl_opponents)

            lineup.append((boy_player, girl_player, boy_opponent, girl_opponent))
            working_pool.remove(boy_player)
            working_pool.remove(girl_player)
            working_pool.remove(boy_opponent)
            working_pool.remove(girl_opponent)

        if len(working_pool) < 4:
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
        if len(working_pool) > 0:
            print('BYEs: {}'.format(', '.join(['{} ({})'.format(name(x), dfi(x))  for x in working_pool])))
        return lineup
    else:
        print('Couldnt find anything')
        return None

    

players = read_roster()
read_results()
show_results()
pair_from_pool(winners, 'WINNERS')
pair_from_pool(losers, 'LOSERS')
