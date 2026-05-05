import numpy as np
import time
import csv

def h2h(ng, np):
    cont = 1
    while cont:
        try:
            hh = h2h_details(ng, np)
            cont = 0
        except Exception:
            ''
    return hh

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

def switch_first_game(tbls, pl):
    t = 0
    while tbls[0,0,t] != pl and tbls[0,1,t] != pl:
        t += 1
    a = tbls[0,0,t]
    tbls[0,0,t] = tbls[0,1,t]
    tbls[0,1,t] = a
    return tbls

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

def gen_rr(num_games, num_players):
    hh = h2h(num_games, num_players)
    tbl, unq, cnt = get_tbls(num_games, num_players, hh)
    matches = balance_tbls(num_games, num_players, tbl, cnt, unq)
    matches_names = np.array([[['a'*30 for x in range(int(num_players/2))] for y in range(2)] for z in range(num_games)])
    for x, X in enumerate(matches):
        for y, Y in enumerate(X):
            for z, Z in enumerate(Y):
                matches_names[x, y, z] = players[Z]
    return matches_names

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

if __name__ == "__main__":
  players = ['Chris H.', 'Scott', 'Michael', 'Justin', 'Roy', 'Brian', 'Patrick', 'Lukas', 'Christian',
           'Dave','Carter', 'Chris W.', 'Mackenzie', 'Nicholas','Jonathan', 'Ben','Paul','Lynne']
  num_players = len(players)
  num_games = 4
  matches_names = gen_rr(num_games, num_players)
  write_bracket(matches_names)
