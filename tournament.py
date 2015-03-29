#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random
import math

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=swiss_style")


'''def executeQuery(query, value1=None, value2=None):
    rows = ['empty']
    DB_connection = connect()
    cur = DB_connection.cursor()
    if value1 is not None and value2 is None:
        cur.execute(query, (value1,))
    elif value1 is not None and value2 is not None:
        cur.execute(query, (value1, value2,))
    else:
        cur.execute(query)
    DB_connection.commit()
    try:
        rows = cur.fetchall()
    except psycopg2.ProgrammingError:
        print('No row to return')
    DB_connection.close()
    return rows
'''

def executeQuery(query, values=None):
    rows = ['empty']
    DB_connection = connect()
    cur = DB_connection.cursor()
    if values is not None:
        cur.execute(query, values)
    else:
        cur.execute(query)
    DB_connection.commit()
    try:
        rows = cur.fetchall()
    except psycopg2.ProgrammingError:
        print('No row to return')
    DB_connection.close()
    return rows

def registerTournament(name):
    print("Calling registerTournament - registering a tournament named: {0}".format(name))
    query = "INSERT INTO tournaments (tournament_name) values (%s) RETURNING tournament_id;"
    values = (name,)
    row = executeQuery(query, values)
    print(row)
    return row[0][0]

def deleteMatches():
    """Remove all the match records from the database."""
    query = "DELETE FROM swiss_pairs"
    executeQuery(query)
    query = "DELETE FROM match_list"
    executeQuery(query)
    query = "DELETE FROM winners_list"
    executeQuery(query)

def deletePlayers():
    """Remove all the player records from the database."""
    sub_query = "SELECT player_id from players"
    rows = executeQuery(sub_query)
    for row in rows:
        deleteSpecificPlayer(row[0])

def deleteSpecificPlayer(player_id):
    print("Deleting player of id {0}".format(player_id))
    query = "DELETE FROM players where player_id = %s"
    values = (player_id, )
    executeQuery(query, values)

def countPlayers():
    print("Calling countPlayers")
    """Returns the number of players currently registered."""
    query = "SELECT count(*) from players;"
    row = executeQuery(query)
    return row[0][0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    print("Calling registerPlayer - registering a player named: {0}".format(name))
    query = "INSERT INTO players (player_name) values (%s) RETURNING player_id;"
    values = (name, )
    row = executeQuery(query, values)
    return row[0][0]

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    query = "SELECT " \
            "tournament_contestants.tournament_id, " \
            "players.player_id, " \
            "players.player_name, " \
            "matches.matches, wins.wins " \
            "FROM tournament_contestants, " \
            "players, " \
            "(SELECT tournament_contestants.tournament_id, " \
            "tournament_contestants.player_id, " \
            "count(match_list.match_id) as matches " \
            "FROM tournament_contestants, match_list " \
            "WHERE tournament_contestants.player_id = match_list.player_id and " \
            "tournament_contestants.tournament_id = match_list.tournament_id " \
            "GROUP BY tournament_contestants.tournament_id, " \
            "tournament_contestants.player_id " \
            "ORDER BY tournament_contestants.tournament_id) as matches, " \
            "(SELECT tournament_contestants.tournament_id, " \
            "tournament_contestants.player_id, " \
            "count(swiss_pairs.match_id) as wins " \
            "FROM tournament_contestants left join swiss_pairs " \
            "on tournament_contestants.player_id = swiss_pairs.winner_id and " \
            "tournament_contestants.tournament_id = swiss_pairs.tournament_id " \
            "GROUP BY tournament_contestants.tournament_id, " \
            "tournament_contestants.player_id " \
            "ORDER BY tournament_contestants.tournament_id) as wins " \
            "WHERE players.player_id = matches.player_id and " \
            "players.player_id = wins.player_id and " \
            "tournament_contestants.tournament_id = matches.tournament_id and " \
            "tournament_contestants.tournament_id = wins.tournament_id and " \
            "tournament_contestants.player_id = players.player_id " \
            "ORDER BY tournament_contestants.tournament_id asc, wins.wins desc;"
    rows = executeQuery(query)
    return rows;

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

def getPlayerId(name):
    query = "select player_id from players where player_name = %s;"
    values = (name, )
    rows = executeQuery(query, values)
    if len(rows) > 0:
        return rows[0][0]
    else: return 'Not found'

def registerContestants(player, tournament):
    print("Calling registerContestants - To the tournament id: {0} adding a player id: {1}".format(tournament, player))
    value = str(player) + ', ' + str(tournament)
    query = "INSERT INTO tournament_contestants values (%s, %s);"
    values = (tournament, player, )
    executeQuery(query, values)

def swissPairings():
    query = "SELECT a.player_id, b.player_id from match_list as a, match_list as b " \
            "where a.match_id = b.match_id and a.tournament_id = b.tournament_id " \
            "and a.player_id < b.player_id"
    rows = executeQuery(query)
    print("the match list is: {0}".format(rows))

    ''' Logic:  1. get list of tournaments (select * from tournaments)
                1b. get the number of players in tournament, to calculate the number of rounds to play
                2. get list of players in that tournament (player_id from tournament_contestants table)
                3. sort the list of players by points (player_points is in players table)
                4. make pairs of players list (getPlayerPairs function)
                5. determine winner (randomly select winner from pair?)
                6. insert pairs into swiss_pairs table, return the match_id (swiss_pairs table)
                7. insert match_id and player_ids for both players in match into match_list
                8. Update the winner's points in tournament_contestants table
    '''
    tournaments_list =[]
    players_list =[]

    # 1. get list of tournaments (select * from tournaments)
    query = "SELECT tournament_id from tournaments order by tournament_id asc"
    tournaments = executeQuery(query)

    for tourney in tournaments:
        # 1b. get the number of players in tournament, to calculate the number of rounds to play
        query = "SELECT count(*) from tournament_contestants where tournament_id = %s"
        values = (tourney, )
        count_players = executeQuery(query, values)
        # there are log2(players) number of rounds
        total_rounds = math.log(count_players[0][0], 2)
        rounds = 1
        while rounds <= total_rounds:
            # 2. get list of players in that tournament (player_id from tournament_contestants table)
            # 3. sort the list of players by points (player_points is in tournament_contestants)
            query = "SELECT player_id from tournament_contestants where tournament_id = %s order by player_points desc"
            values = (tourney,)
            players_in_tourney = executeQuery(query, values)
            # 4. make pairs of players list (getPlayerPairs function)
            player_pairs = getPlayerPairs(players_in_tourney)
            for pair in player_pairs:
                # 5. determine winner (randomly select winner from pair?)
                won_by = random.choice([1,2,3])
                if won_by is 1:
                    winner_id = pair[0]
                    player1_points = 2
                    player2_points = 0
                elif won_by is 2:
                    winner_id = pair[1]
                    player1_points = 0
                    player2_points = 2
                elif won_by is 3:
                    winner_id = -1
                    player1_points = 1
                    player2_points = 1

                # 6. insert pairs into swiss_pairs table, return the match_id (swiss_pairs table)
                query = "INSERT into swiss_pairs (tournament_id, player1_id, player2_id, round, winner_id) values (%s, %s, %s, %s, %s) RETURNING match_id"
                values = (tourney, pair[0], pair[1], rounds, winner_id)
                match_id_row = executeQuery(query, values)
                match_id = match_id_row[0][0]
                # 7. insert match_id and player_ids for both players in match into match_list
                query = "INSERT into match_list values (%s, %s, %s)"
                values = (tourney, match_id, pair[0])
                executeQuery(query, values)
                values = (tourney, match_id, pair[1])
                executeQuery(query, values)
                # 8. Update the winner's points in tournament_contestants table
                query = "UPDATE tournament_contestants SET player_points = player_points + %s where tournament_id = %s and player_id = %s"
                values = (player1_points, tourney, pair[0])
                executeQuery(query, values)
                values = (player2_points, tourney, pair[1])
                executeQuery(query, values)
            print("After round # {0} the player standings are: ".format(rounds))
            print(playerStandings())
            rounds += 1



def getPlayerPairs(players):
    ''' Returns a list of tuples '''
    players.reverse()
    player_pairs = []
    while len(players) > 0:
        player_pairs.append((players.pop(), players.pop()))
    return player_pairs

def main():

    tournament_id = registerTournament("Hand's tourney")
    print("- Registered tournament, id given is: {0}".format(tournament_id))

    tournament_id2 = registerTournament("Trial By Combat")
    print("- Registered tournament, id given is: {0}".format(tournament_id))

    player_id = registerPlayer("The Mountain")
    print("- Registered player, id given is: {0}".format(player_id))
    registerContestants(player_id, tournament_id2)
    registerContestants(player_id, tournament_id)

    player_id = registerPlayer("The Hound")
    registerContestants(player_id, tournament_id)
    print("- Registered player, id given is: {0}".format(player_id))

    player_id = registerPlayer("Ser Loras")
    registerContestants(player_id, tournament_id)
    print("- Registered player, id given is: {0}".format(player_id))

    player_id = registerPlayer("Ser Jaime")
    registerContestants(player_id, tournament_id)
    print("- Registered player, id given is: {0}".format(player_id))

    player_id = registerPlayer("Oberyn Martell")
    registerContestants(player_id, tournament_id2)

    print("total players are: {0}".format(countPlayers()))

    swissPairings()
    #deleteMatches()
    #print('The student id for {0} is {1}'.format('Prasana Shevade', id1))
    #print('The student id for {0} is {1}'.format('Gauri Jog', id2))
    #print('The student id for {0} is {1}'.format('Udayan Shevade', id3))


if __name__ == '__main__':
    main()
