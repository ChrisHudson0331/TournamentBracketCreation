# TournamentBracketCreation
In this repository is code and sample outputs for generating brackets for Chess and Catan tournaments.

## Chess Bracket
In the main function of the python file for generating the Chess bracket are two variables, players and num_games. The players variable is a list of players participating in the tournament. It must be an even number of players, if there are an odd number of players then a "nobody" player must be added so that the person playing nobody can be identified in each round. The num_games variable is the number of round robin games for the tournament. It must also be an even number or the program will get stuck in an infinite loop while trying to balance the number of black and white games everyone plays.
The program will randomize the matchups ensuring nobody plays a player more than 1 time and that the number of times playing black and white is even for each player. The output of the program is a csv file with the tournament match ups. A sample tournament matchup is in the repository for reference.

## Catan Bracket
In the main function of the python file for generating the Catan bracket are two variables, players and num_rounds. The players variable is a list of players who will be playing in the Catan tournament and the num_rounds variable is the number of rounds that will make up the tournament.
The program generates random groupings of 3 or 4 for each round and outputs the bracket in a csv file, a sample of which is shown in the repo. It is ensured that everyone plays a balanced number of 3 player games and steps are taken to minimize the number of times players play the same people many times over.
