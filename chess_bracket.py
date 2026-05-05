import numpy as np
import time
import csv

# This function executes the h2h_details() function. Since h2h_details() occassionally throws an Exception when it encounters an infinite loop, this 
# function is needed to catch those Exceptions and tell h2h_details() to try it's procedure again.
def h2h(ng, np):
    cont = 1
    while cont:
        try:
            hh = h2h_details(ng, np)
            cont = 0
        except Exception:
            ''
    return hh

# This function generates random matchups for the chess tournament. The output is head2head which is a matrix of shape (num_players, num_games) who's
# elements are the index of the given matchup. Hence head2head[i,j] = k implies player i faces player k on game j. It follows that head2head[i,j] = k
# implies that head2head[k,j] = i and i != k. 
# The procedure for generating these random matchups occassionally generates infinite loops. In this case the function terminates throwing an Exception. 
# This gets caught in the h2h() function which then orders this function to start over.
def h2h_details(num_games, num_players):
    head2head = np.zeros((num_players, num_games)) + num_players + 1
    for player in range(num_players):
        for game in range(num_games):
            if head2head[player, game] == num_players + 1:
                opponent = np.random.randint(player + 1, num_players)
                head2head[player, game] = opponent
                start = time.time()
                while head2head[opponent, game] < num_players + 1 or opponent in head2head[player, :game]:
                    opponent = np.random.randint(player + 1, num_players)
                    head2head[player, game] = opponent
                    if time.time() - start > 0.1:
                        raise Exception("Bad Solution")
                head2head[opponent, game] = player
    return head2head

# The key output of this function is tables, a (num_games, 2, num_boards) dimensional tensor tables where tables[i,j,k] = m corresponds to player m playing
# game i with colour j on board k. The tables tensor is constructed from the head2head matrix of size (num_players, num_games). head2head[i,j] = k
# indicates players i and k play each other on game j, it also implies that head2head[k,j] = i and i != k. The function transforms head2head[i,j] = k into
# tables[j,0,m] = i or k and tables[j,1,m] = k or i. That is to say, the function randomly assigns a board and colours to each matchup.
# unique is a list of all player indices and counts[i] = j indicates player i is white j times given the generated tables tensor.
def get_tbls(num_games, num_players, head2head):
    num_tables = int(num_players/2)
    unique = np.array(range(num_players))
    counts = np.zeros(num_players)
    tables = np.random.randint(num_players, size = (num_games, 2, num_tables))
    for game in range(num_games):
        for table in range(num_tables):
            p1 = tables[game, 0, table]
            p2 = head2head[p1, game]
            while p1 in tables[game, 0, :table] or p2 in tables[game, 0, :table]:
                tables[game, 0, table] = np.random.randint(num_players)
                p1 = tables[game, 0, table]
                p2 = head2head[p1, game]
            tables[game, 1, table] = p2
    unq, cnts = np.unique(tables[:,0,:], return_counts=True)
    for ui, ue in enumerate(unq):
        counts[ue] = cnts[ui]
    return tables, unique, counts

# A niche shortcut function called by balance_tbls that is not critical for understanding the program logic. If a player is always black or white then
# This function is called and their colour is switched in their first match.
def switch_first_game(tbls, pl):
    t = 0
    while tbls[0,0,t] != pl and tbls[0,1,t] != pl:
        t += 1
    a = tbls[0,0,t]
    tbls[0,0,t] = tbls[0,1,t]
    tbls[0,1,t] = a
    return tbls

# This function randomly swaps the colours of the tables tensor with shape (num_games, 2, num_boards) until everyone plays black and white the same number
# of times. tables[i,j,k] = m indicates player m plays game i with colour j on board k.
# Note that if num_games is an odd number then this function will loop forever.
def balance_tbls(num_games, num_players, tables, counts, unique):
    evenbw = counts == int(num_games/2)
    while False in evenbw:
        for player in range(num_players):
            if evenbw[player] == False:
                if counts[player] == num_games or counts[player] == 0:
                    tables = switch_first_game(tables, player)
                bw = 0
                if counts[player] < int(num_games/2):
                    bw = 1
                game = np.random.randint(num_games)
                while player not in tables[game, bw, :]:
                    game = np.random.randint(num_games)
                table = 0
                while tables[game, bw, table] != player:
                    table += 1
                a = tables[game, bw, table]
                tables[game, bw, table] = tables[game, (bw + 1)%2, table]
                tables[game, (bw + 1)%2, table] = a
                unq, cnts = np.unique(tables[:,0,:], return_counts=True)
                for ui, ue in enumerate(unq):
                    counts[ue] = cnts[ui]
                evenbw = counts == int(num_games/2)
    return tables

# This function generates a randomized round robin matchup list in the form matches_names = (num_games, 2, num_boards). Each element of matches_names
# are player names and their index dictates the game, board and colour the player is playing.
# h2h generates the randomized head to head player matches while ensuring players are only paired together a maximum of 1 time. The output from this
# function hh is a matrix of shape (num_players, num_games). The element hh[i,j] equals an integer k indicating player i plays player k on game j.
# Hence it is always the case that i != k and hh[i,j] = k implies hh[k,j] = i.
# get_tbls randomly assigns each matchup to a board. The hh matrix is converted to the tbl tensor with shape (num_games, 2, num_boards). The elements of
# this tensor are player indices. tbl[i,j,k] = m corresponds to player m playing game i with colour j on board k. If hh[i,j] = m then tbl[j,0,k] = i or m
# and tbl[j,1,k] = m or i.
# unq is the list of player indices ranging from 0 to num_players - 1 and cnt is the count of number of times a given player index is playing white.
# balance_tbls randomly swaps who is playing black and who is playing white such that everyone plays an equal number of games as black and white. The
# resulting tensor matches is almost identical to the tbl tensor only with some colours swapped.
# The rest of the function creates the matches_names tensor which is identical to the matches tensor only with the player indices replaced with player
# names.
def gen_rr(num_games, num_players, players):
    hh = h2h(num_games, num_players)
    tbl, unq, cnt = get_tbls(num_games, num_players, hh)
    matches = balance_tbls(num_games, num_players, tbl, cnt, unq)
    matches_names = np.array([[['a'*30 for x in range(int(num_players/2))] for y in range(2)] for z in range(num_games)])
    for x, X in enumerate(matches):
        for y, Y in enumerate(X):
            for z, Z in enumerate(Y):
                matches_names[x, y, z] = players[Z]
    return matches_names

# This function outputs a stylized csv file based on a given round robin matchup list. matches_names has the shape (num_games, 2, num_boards) and the
# elements are player names. The indices indicate the board and game of each matchup and whether the player is playing white or black.
def write_bracket(matches_names):
    matches_names.shape
    num_games = matches_names.shape[0]
    num_boards = matches_names.shape[2]
    bracket = np.full((num_games*3, num_boards + 1), '', dtype=object)
    bracket[1::3,0] = 'White'
    bracket[2::3,0] = 'Black'
    bracket[0,0] = ''
    for i in range(1, num_boards + 1):
        bracket[0,i] = 'Board ' + chr(ord('A') + i - 1)
        bracket[1::3,i] = matches_names[:,0,i-1]
        bracket[2::3,i] = matches_names[:,1,i-1]
    np.savetxt("chess_matchups.csv", bracket, delimiter=",", fmt="%s")

# The variable players must be filled in with the list of players partaking in the tournament. The program assumes the number of players is even so 
# a "no player" slot should be filled if there are an odd number of players in the tournament. 
# num_games is the number of games to be played in the round robin. It must be even to balance the number of black and white games each player has.
# Given the player list and num_games, gen_rr generates the round robin bracket and write_bracket creates a nicely stylized csv file based on the
# generated bracket.
if __name__ == "__main__":
  players = ['Chris H.', 'Scott', 'Michael', 'Justin', 'Roy', 'Brian', 'Patrick', 'Lukas', 'Christian',
           'Dave','Carter', 'Chris W.', 'Mackenzie', 'Nicholas','Jonathan', 'Ben','Paul','Lynne']
  num_players = len(players)
  num_games = 4
  matches_names = gen_rr(num_games, num_players, players)
  write_bracket(matches_names)






