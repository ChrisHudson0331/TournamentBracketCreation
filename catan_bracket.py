import numpy as np

def get_players_matrix(num_rounds, player_list):
    num_players = len(player_list)
    matrix_index = np.array([np.random.permutation(num_players).tolist() for _ in range(num_rounds)])
    matrix_players = np.array([np.array(['x'*100 for _ in range(num_players)]) for _ in range(num_rounds)])
    for i in range(num_rounds):
        for j in range(num_players):
            matrix_players[i,j] = player_list[matrix_index[i,j]]
    return matrix_players

def get_player_weights(player_list, num_rounds, num_players, num_3p, players_matrix):
    player_weights = {player:0 for player in player_list}
    for rnd in range(num_rounds):
        for position in range(num_players):
            weight = 1
            if position < num_3p*3:
                weight = 0
            player_weights[players_matrix[rnd,position]] += weight
    return player_weights

def swap_matrix_elements(matrix, r, c1, c2):
    swap = matrix[r,c1]
    matrix[r,c1] = matrix[r,c2]
    matrix[r,c2] = swap
    return matrix

def get_player_indices(player, players_matrix):
    return [list(players_matrix[x]).index(player) for x in range(len(players_matrix))]

def balance_weights(player_weights, players_matrix, num_players):
    mean_weight = sum(player_weights.values())/num_players
    for player in player_weights.keys():
        diff = player_weights[player] - mean_weight
        if abs(diff) > 1:
            indices = get_player_indices(player, players_matrix)
            if diff < 0:
                players_matrix = swap_matrix_elements(players_matrix, indices.index(min(indices)), 
                                                      min(indices), num_players - 1)
            else:
                players_matrix = swap_matrix_elements(players_matrix, indices.index(max(indices)), 
                                                      max(indices), 0)
            return players_matrix, False
    return players_matrix, True
    
def get_balanced_players_matrix(num_rounds, num_players, num_3p, num_balance_trys = 10):
    balance_try = 0
    players_matrix = get_players_matrix(num_rounds, player_list)
    balanced_weights = False
    while balanced_weights == False:
        player_weights = get_player_weights(player_list, num_rounds, num_players, num_3p, players_matrix)
        players_matrix, balanced_weights = balance_weights(player_weights, players_matrix, num_players)
        balance_try += 1
        if balance_try > num_balance_trys:
            balance_try = 0
            players_matrix = get_players_matrix(num_rounds, player_list)
    return players_matrix

def get_game_indices(gm, num_3p):
    if gm < num_3p:
        return [gm*3, gm*3 + 2]
    return [gm*4 - num_3p, gm*4 - num_3p + 3]

def get_correlation_score(num_players, num_rounds, num_games, num_3p, player_list, players_matrix):
    correlation_matrix = np.zeros((num_players, num_players))
    for rnd in range(num_rounds):
        for gm in range(num_games):
            game_indices = get_game_indices(gm, num_3p)
            for p1 in range(game_indices[0], game_indices[1] + 1):
                for p2 in range(game_indices[0], game_indices[1] + 1):
                    p1_index = player_list.index(players_matrix[rnd,p1])
                    p2_index = player_list.index(players_matrix[rnd,p2])
                    correlation_matrix[p1_index, p2_index] += 1
    return sum(sum(correlation_matrix**2))

def get_uncorrelated_matrix(num_players, num_rounds, num_games, num_3p, player_list, num_matrices = 100):
    players_matrix = get_balanced_players_matrix(num_rounds, num_players, num_3p)
    correlation_score = get_correlation_score(num_players, num_rounds, num_games, num_3p, player_list, players_matrix)
    for i in range(num_matrices):
        new_matrix = get_balanced_players_matrix(num_rounds, num_players, num_3p)
        new_score = get_correlation_score(num_players, num_rounds, num_games, num_3p, player_list, new_matrix)
        if new_score < correlation_score:
            correlation_score = new_score
            players_matrix = new_matrix
    return players_matrix

def write_bracket(players_matrix, num_rounds, num_games, num_3p):
    bracket = np.full((num_rounds*5, num_games + 1), '', dtype=object)
    for i in range(1, num_games + 1):
        bracket[0,i] = 'Board ' + chr(ord('A') + i - 1)
    for i in range(num_rounds):
        bracket[1 + i*5, 0] = 'Game ' + str(i + 1)
    players_matrix_3p = players_matrix[:,0:3*num_3p]
    players_matrix_4p = players_matrix[:,3*num_3p:]
    for i in range(num_3p):
        for j in range(num_rounds):
            for k in range(3):
                bracket[5*j+1+k,i+1] = players_matrix_3p[j,3*i+k]
    for i in range(num_games - num_3p):
        for j in range(num_rounds):
            for k in range(4):
                bracket[5*j+1+k,i+1+num_3p] = players_matrix_4p[j,4*i+k]
    np.savetxt("catan_matchups.csv", bracket, delimiter=",", fmt="%s")

if __name__=="__main__":
  
  player_list = ['Chris','Christian','Claire','Lukas','Siobhan','Reid','Justin','Alexandre','Burney','Scott','Derek','Joey',
                'Roy','Lynne','Mackenzie','Kate','Thomas','Sofie','Brian','Jordyn','Ben','Iain','Abin','Patrick',
                'Evan','Nicholas']
  num_rounds = 3
  
  num_players = len(player_list)
  num_3p = 4 - num_players % 4
  num_games = int(num_players / 4) + 1
  if num_3p == 4:
      num_3p = 0
      num_games -= 1    
  players_matrix = get_uncorrelated_matrix(num_players, num_rounds, num_games, num_3p, player_list)
  write_bracket(players_matrix, num_rounds, num_games, num_3p)
