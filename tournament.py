#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


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
    query = "INSERT INTO players (player_name, player_points) values (%s, %s) RETURNING player_id;"
    values = (name, str(0))
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
    '''
    query = "SELECT tournament_name, player_name from tournaments, players, tournament_contestants where tournament_contestants.player_id = players.player_id and tournament_contestants.tournament_id = tournaments.tournament_id"
    rows = executeQuery(query)
    for row in rows:
        print("The tournament name is: {0} and the player is: {1}".format(row[0], row[1]))
    '''
    tournaments_list =[]
    players_list =[]
    query = "SELECT tournament_id from tournaments order by tournament_id asc"
    tournaments = executeQuery(query)
    for tourney in tournaments:
        query = "SELECT player_id from tournament_contestants where tournament_id = %s"
        values = (tourney,)
        players_in_tourney = executeQuery(query, values)
        for count in range(0, len(players_in_tourney)-1):
            query = "INSERT into swiss_pairs (tournament_id, player1_id, player2_id, round) values (%s, %s, %s, %s) RETURNING match_id"
            values = (tourney, players_in_tourney[count], players_in_tourney[count+1], 0)
            match_id_row = executeQuery(query, values)
            query = "INSERT into match_list values (%s, %s, %s)"
            values = (tourney, match_id_row[0][0], players_in_tourney[count])
            executeQuery(query, values)
            values = (tourney, match_id_row[0][0], players_in_tourney[count+1])
            executeQuery(query, values)

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
    #deletePlayers()
    #print('The student id for {0} is {1}'.format('Prasana Shevade', id1))
    #print('The student id for {0} is {1}'.format('Gauri Jog', id2))
    #print('The student id for {0} is {1}'.format('Udayan Shevade', id3))


if __name__ == '__main__':
    main()
