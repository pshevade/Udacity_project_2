#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random
import math
import pprint

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

def countPlayersInTournament(tournament):
    tournament_id = getTournamentID('Default')
    query = "SELECT count(*) from tournament_contestants where tournament_id = %s"
    values = (tournament_id, )
    rows = executeQuery(query, values)
    return rows[0][0]

def registerPlayer(name, tournament=None):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).

    Logic -
            1. check if tournament exists, else create it.
            1b. if no tournament doesn't exist, create it
            1c. if no tournament parameter given and default doesn't exist, create it
            2. register players
            3. register player and tournament in tournament_contestants
    """
    # 1. check if tournament exists:
    if tournament is not None:
        tournament_id = getTournamentID(tournament)
        if tournament_id >0:
            pass
        else:
            # 1b. if tournament doesn't exist, create it
            tournament_id = registerTournament(tournament)
    elif tournament is None:
        tournament_id = getTournamentID('Default')
        if tournament_id >0:
            pass
        else:
            # 1b. if tournament doesn't exist, create it
            tournament_id = registerTournament('Default')

    # 2. register player
    print("Calling registerPlayer - registering a player named: {0}".format(name))
    query = "INSERT INTO players (player_name) values (%s) RETURNING player_id;"
    values = (name, )
    row = executeQuery(query, values)
    player_id = row[0][0]

    # 3. register player and tournament in tournament_contestants
    registerContestants(player_id, tournament_id)
    return player_id

def getTournamentID(tournament):
    query = "select tournament_id from tournaments where tournament_name = %s"
    values = (tournament, )
    rows = executeQuery(query, values)
    # 1.b if no tournament doesn't exit, create it
    if len(rows) is not 0:
        tournament_id = rows[0][0]
    else:
        print("No tournament exits, may need to tournament {0}".format(tournament))
        tournament_id = -1
    return tournament_id

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
    query = "SELECT tournament_id, tournament_name from tournaments order by tournament_id asc"
    tournaments = executeQuery(query)
    standings = []
    for tourney in tournaments:
        print("For tournament: {0}".format(tourney[1]))
        query = "SELECT player_id, player_name, wins, matches from getMatchesAndWins where tournament_id = %s"
        values = (tourney[0],)
        rows = executeQuery(query, values)
        pp = pprint.PrettyPrinter(indent = 8, depth = 4)
        for row in rows:
            pp.pprint('{0} {1} {2} {3}'.format(row[0], row[1], row[2], row[3]))
        standings.append(rows)
    print standings;
    print("The length of the standings list is: {0}".format(len(standings)))
    if len(standings) > 1:
        print("returning all standings")
        return standings
    else:
        return standings[0]


def reportMatch(winner, loser, tournament=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if tournament is not None:
        tournament_id = getTournamentID(tournament)
    else:
        tournament_id = getTournamentID('Default')
    query = "INSERT into match_list (tournament_id, winner_id, loser_id) values (%s, %s, %s)"
    values = (tournament_id, winner, loser,)
    rows = executeQuery(query, values)

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

def swissPairings(tournament=None):
    ''' Logic:
            1. get tournament_id
            2. for tournament_id, check if each player has played the same number of matches
            3. if each player has played the same number of matches, check if matches played = max
                note:   total rounds = log(2) n         where n players
                        total matches = log(2) n x n    where n players
            4. generate swiss pairing by sorting players by standing
            5. reassemble list based on OMW in case of tie
    '''

    if tournament is not None:
        count_players = countPlayersInTournament(tournament)
        tournament_id = getTournamentID(tournament)
    else:
        count_players = countPlayersInTournament('Default')
        tournament_id = getTournamentID('Default')
    print("The players in this tournament are: {0}".format(count_players))
    total_rounds = math.log(count_players, 2)
    total_matches = total_rounds * count_players
    player_pairs = []
    print("THe Tournament id is: {0}".format(tournament_id))
    query = "select getMatches.player_id, getMatches.matches from getMatches where getMatches.tournament_id = %s"
    values = (tournament_id, )
    rows = executeQuery(query, values)
    print("Raw rows with player/match info from db: {0}".format(rows))
    matches_played = [row[1] for row in rows]
    print("matches played by all: {0}".format(matches_played))

    all_played_same_matches = all(x == matches_played[0] for x in matches_played)
    if all_played_same_matches:
        if matches_played[0] == total_matches:
            print("We have played all the matches possible in this Swiss Style Tournament")
        else:
            query = "select getWins.player_id, players.player_name from getWins, players where players.player_id = getWins.player_id order by getWins.wins"
            rows = executeQuery(query)
            player_pairs = getPlayerPairs(rows)
    else:
        print("We have players who still haven't played in this round...")
        for row in rows:
            print("Player ID: {0} has played {1} matches".format(row[0], row[1]))
    print ("The player pairs are: {0}".format(player_pairs))
    return player_pairs

def getPlayerPairs(players):
    ''' Returns a list of tuples '''
    players.reverse()
    player_pairs = []
    while len(players) > 0:
        player_pairs.append((players.pop() + players.pop()))
    return player_pairs

def test(tournament):
    # 1. check if tournament exists:
    query = "select tournament_id from tournaments where tournament_name = %s"
    if tournament is not None:
        values = (tournament, )
    elif tournament is None:
        values = ('Default', )
    rows = executeQuery(query, values)
    if len(rows) is not 0:
        tournament_id = rows
        print('Here are the rows: {0}'.format(tournament_id))
    else:
        print("Empty row!")

def main():

    registerPlayer("The Mountain", "Hand's tourney")
    registerPlayer("Brienne of Tarth", "Hand's tourney")
    registerPlayer("Jorah Mormont", "Hand's tourney")
    registerPlayer("Oberyn Martell", "Hand's tourney")
    registerPlayer("Baristan Selmy", "Hand's tourney")
    registerPlayer("Robert Baratheon", "Hand's tourney")
    registerPlayer("Jaime Lanister", "Hand's tourney")
    registerPlayer("The Hound", "Hand's tourney")

    registerPlayer("Prasanna Shevade")
    registerPlayer("Gauri Jog")
    registerPlayer("Shrikant Shevade")
    registerPlayer("Udayan Shevade")

    print("Player's standings before tournament starts")
    playerStandings()

    swissPairings()

    print("Player's standings after tournament ends")
    playerStandings()
    '''

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

    player_id = registerPlayer("Loras Tyrell")
    registerContestants(player_id, tournament_id)
    print("- Registered player, id given is: {0}".format(player_id))

    player_id = registerPlayer("Jaime Lannister")
    registerContestants(player_id, tournament_id)
    print("- Registered player, id given is: {0}".format(player_id))

    player_id = registerPlayer("Oberyn Martell")
    registerContestants(player_id, tournament_id2)

    player_id = registerPlayer("Tyrion Lannister")
    registerContestants(player_id, tournament_id2)

    player_id = registerPlayer("Bronn Sellsword")
    registerContestants(player_id, tournament_id2)

    player_id = registerPlayer("Baristan Selmy")
    registerContestants(player_id, tournament_id)

    player_id = registerPlayer("Meryn Trant")
    registerContestants(player_id, tournament_id)

    player_id = registerPlayer("Jorah Mormont")
    registerContestants(player_id, tournament_id2)

    player_id = registerPlayer("Davos Seaworth")
    registerContestants(player_id, tournament_id2)

    print("total players are: {0}".format(countPlayers()))
    #swissPairings()

    playerStandings()
    '''



    #deleteMatches()
    #print('The student id for {0} is {1}'.format('Prasana Shevade', id1))
    #print('The student id for {0} is {1}'.format('Gauri Jog', id2))
    #print('The student id for {0} is {1}'.format('Udayan Shevade', id3))


if __name__ == '__main__':
    main()
