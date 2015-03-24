#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=swiss_style")


def executeQuery(query, value1=None, value2=None):
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


def registerTournament(name):
    print("Calling registerTournament - registering a tournament named: {0}".format(name))
    query = "INSERT INTO tournaments (tournament_name) values (%s) RETURNING tournament_id;"
    row = executeQuery(query, name)
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
    executeQuery(query, player_id)

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
    query = "INSERT INTO players (player_name, player_points) values (%s, 0) RETURNING player_id;"
    row = executeQuery(query, name)
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
    rows = executeQuery(query, name)
    if len(rows) > 0:
        return rows[0][0]
    else: return 'Not found'

def registerContestants(player, tournament):
    print("Calling registerContestants - To the tournament id: {0} adding a player id: {1}".format(tournament, player))
    value = str(player) + ', ' + str(tournament)
    query = "INSERT INTO tournament_contestants values ({0}, {1});".format(player, tournament)
    executeQuery(query)

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    '''query = "SELECT tournament_id FROM tournaments"
    t_id_rows = executeQuery(query)
    print('This is what the tournament id rows look like: ')
    print(t_id_rows)
    query = "SELECT player_id FROM tournament_contestants WHERE tournament_id = %s"
    for tournament_ids in t_id_rows:
        p_id_rows = executeQuery(query, tournament_ids)
        query = "SELECT count(*) FROM tournament_contestants WHERE tournament_id =%s"
        count_players = executeQuery(query, tournament_ids)
        print("this is the tournament_contestants table for tournament_id {0}: ".format(tournament_ids))
        print(p_id_rows)
        for id1 in range(0, count_players[0][0]):
            for id2 in range(id1, count_players[0][0]):
                query = "SELECT match_id from swiss_pairs WHERE player1_id = %s and player2_id = %s"
                match_rows = executeQuery(query, id1, id2)
                print("For players {0} and {1} we found that they played match {2}: ".format(id1, id2, match_rows))
        #for player in p_id_rows:
    '''
    query = "SELECT a.player_id, b.player_id from match_list as a, match_list as b "
            "where a.match_id = b.match_id and a.tournament_id = b.tournament_id "
            "and a.player_id < b.player_id"
    rows = executeQuery(query)
    print("the match list is: {0}".format(rows))

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
