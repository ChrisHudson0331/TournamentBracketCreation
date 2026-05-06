import numpy as np

# Generate a random matrix_players of shape (num_rounds, num_players). Each round contains a list of all the players in a random order. This is the base
# bracket for the Catan tourney.
def get_players_matrix(num_rounds, player_list):
    num_players = len(player_list)
    matrix_index = np.array([np.random.permutation(num_players).tolist() for _ in range(num_rounds)])
    matrix_players = np.array([np.array(['x'*100 for _ in range(num_players)]) for _ in range(num_rounds)])
    for i in range(num_rounds):
        for j in range(num_players):
            matrix_players[i,j] = player_list[matrix_index[i,j]]
    return matrix_players

# This function returns a dictionary indicating the number of times each player plays a 3 player game given the players_matrix, a matrix of shape 
# (num_rounds, num_players) whose first 3*num_3p players in a round are in groups of 3 and everyone else is in groups of 4.
def get_player_weights(player_list, num_rounds, num_players, num_3p, players_matrix):
    player_weights = {player:0 for player in player_list}
    for rnd in range(num_rounds):
        for position in range(num_players):
            weight = 1
            if position < num_3p*3:
                weight = 0
            player_weights[players_matrix[rnd,position]] += weight
    return player_weights

# Swaps the matrix elements matrix[r,c1] and matrix[r,c2]
def swap_matrix_elements(matrix, r, c1, c2):
    swap = matrix[r,c1]
    matrix[r,c1] = matrix[r,c2]
    matrix[r,c2] = swap
    return matrix

# Returns a list of the indices of the player for each round
def get_player_indices(player, players_matrix):
    return [list(players_matrix[x]).index(player) for x in range(len(players_matrix))]

# The main inputs of this function are the player_weights and players_matrix. players_matrix is a matrix of shape (num_rounds, num_players) indicating which
# players play each other in which round. The first few players in a given round are grouped into 3 player games and the rest are grouped into 4 player
# games. player_weights is a dictionary indicating the number of times each player plays a 3 player game. If any one player is more than 1 game away from 
# the mean number of 3 player games each player faces, the function will swap that player randomly between a 3 and 4 player grouping, appropriately 
# increasing or decreasing the number of 3 player games that person plays. The function will then return False indicating the weights are not balanced. If 
# the player weights are balanced then this function makes no changes to players_matrix and returns True.
def balance_weights(player_weights, players_matrix, num_players, num_3p):
    mean_weight = sum(player_weights.values())/num_players
    for player in player_weights.keys():
        diff = player_weights[player] - mean_weight
        if abs(diff) > 1:
            indices = get_player_indices(player, players_matrix)
            if diff < 0:
                swap_index = np.random.randint(3*num_3p, num_players)
                players_matrix = swap_matrix_elements(players_matrix, indices.index(min(indices)), 
                                                      min(indices), swap_index)
            else:
                swap_index = np.random.randint(0, 3*num_3p)
                players_matrix = swap_matrix_elements(players_matrix, indices.index(max(indices)), 
                                                      max(indices), swap_index)
            return players_matrix, False
    return players_matrix, True

# This function calls the get_players_matrix function to generate the players_matrix matrix, a (num_rounds, num_players) shaped matrix encoding the Catan
# bracket. For a given round, the first 3*num_3p players are grouped into 3 player games and everyone else is grouped into 4 player games.
# For the generated players_matrix, the function calculates the number of times each player plays a 3 player game in the get_player_weights function.
# If any player plays at least 2 3 player games more than any other player then the weights are unbalanced. The balance_weights function is called which
# appropriately swaps unbalanced players randomly between a 3 and 4 grouping. If a swap occured then the balanced_wieghts variable is returned as False, 
# otherwise it is returned as True.
# By default, the function will try to balance the weights with a maximum of 30 swaps. If this cannot be done then a new players_matrix will be generated.
# The maximum number of swaps the function will try can be set by changing the num_balance_trys variable.
# The resulting balanced players matrix is returned.
def get_balanced_players_matrix(num_rounds, num_players, num_3p, num_balance_trys = 30):
    balance_try = 0
    players_matrix = get_players_matrix(num_rounds, player_list)
    balanced_weights = False
    while balanced_weights == False:
        player_weights = get_player_weights(player_list, num_rounds, num_players, num_3p, players_matrix)
        players_matrix, balanced_weights = balance_weights(player_weights, players_matrix, num_players, num_3p)
        balance_try += 1
        if balance_try > num_balance_trys:
            balance_try = 0
            players_matrix = get_players_matrix(num_rounds, player_list)
    return players_matrix

# This function returns the grouping of 3 or 4 indices corresponding to the game number. Depending on the number of 3 player games the indices will shift.
# For example, if there are 2 3 player games then the indices for game 3 are [6,7,8,9].
def get_game_indices(gm, num_3p):
    if gm < num_3p:
        return [gm*3, gm*3 + 2]
    return [gm*4 - num_3p, gm*4 - num_3p + 3]

# This function returns a score indicating the number of collisions in a Catan bracket specified by the players_matrix. That is to say, the number of times
# players are paired together more than once in the bracket. The lower the number and severity of collisions, the lower the score.
# This is achieved by first building the correlation_matrix. This is a symetrical matrix of shape (num_players, num_players) who's (i,j) elements indicate
# the number of times players i and j play eachother in the tournament.
# The last step in generating the score is to square all the elements in the matrix and then sum up all the numbers. The resulting number is returned.
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

# This function generates a randomized round robin for the Catan players. The output is players_matrix which is a a matrix of shape 
# (num_rounds, num_players) where the ith row is a list which is ordered in groupings of 4 or 3 corresponding to the matchups for that round. The first
# num_3p groupings are of size 3 and the rest of size 4.
# get_balanced_players_matrix generates the players_matrix described above. The matrix is randomized but it is ensured that no player has more than 1 
# 3 player game more or less than any other player.
# get_correlation_score generates a number indicating the number of times players repeatedly play each other in Catan games, in other words it calculates
# the number of collisions in the players_matrix bracket. The fewer the number of collisions the lower the score. Players colliding with eachother many 
# times generates a larger score than many players colliding with each other a few times. For example, if players A and B play 2 games together and
# players C and D also play 2 games together, this will generate a lower score than if players A and B play 3 games together and players C and D play 1 game
# together.
# The function generates many player matrices and generates their correlation scores. The matrix with the lowest correlation score is returned. That is to
# say, the matrix with the fewest and least severe collisions is returned. By default 100 matrices are generated, but this can be adjusted by changing the 
# num_matrices parameter for the function.
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

# The main input to this function is the players_matrix which has a shape (num_rounds, num_players). The list corresponding to players_matrix[i,:] is
# ordered in the round i matchups such that the last 4 people in that list play each other, the second last 4 grouping play each other, etc. The first
# 3*num_3p players play in 3 person groupings instead of 4 person groupings.
# This function creates a numpy matrix called bracket corresponding to a formatted round robin bracket reflecting the players_matrix matchups. The bracket
# numpy matrix is then saved as a csv file to the local directory.
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

# player_list and num_rounds must be specified to the desired values when running this function. player_list is the list of players who will compete
# in the Catan tournament. num_rounds is the number of Catan games each player will play in the round robin.
# get_uncorrelated_matrix returns a random round robin bracket in the form of a matrix of shape (num_rounds, num_players). Each round corresponds to a
# randomized list of players such that the last 4 players in the group plays eachother in that game, the next 4 grouping play eachother and so on. The
# first num_3p*3 names are grouped into games of 3 instead of 4. The function ensures no player plays in 3 player games more than 1 time more than anyone
# else and otherwise minimizes the number of times players play the same player in multiple games.
# write_bracket takes the output of the get_uncorrelated_matrix function and creates a nicely formatted csv file with the round robin matchups. The csv
# file is saved to the local directory.
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
