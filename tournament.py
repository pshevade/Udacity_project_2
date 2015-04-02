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


def executeQuery(query, values=None):
    """ Connect to database and execute the query that is passed
        Parameter 'values' can be a list of n elements, or can be None,
        in which case the query is fully described as is
    """
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
    """Register a tournament, of the name give by parameter 'name'"""
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
    query = "DELETE FROM bye_list"
    executeQuery(query)


def deletePlayers():
    """Remove all the player records from the database."""
    sub_query = "SELECT player_id from players"
    rows = executeQuery(sub_query)
    for row in rows:
        deleteSpecificPlayer(row[0])


def deleteSpecificPlayer(player_id):
    """Deletes a specific player, based on the player_id"""
    query = "DELETE FROM players where player_id = %s"
    values = (player_id, )
    executeQuery(query, values)


def countPlayers():
    """Count all players, across all tournaments"""
    print("Calling countPlayers")
    """Returns the number of players currently registered."""
    query = "SELECT count(*) from players;"
    row = executeQuery(query)
    return row[0][0]


def countPlayersInTournament(tournament):
    """Count all players in a given tournament"""
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
    query = "INSERT INTO players (player_name) values (%s) RETURNING player_id;"
    values = (name, )
    row = executeQuery(query, values)
    player_id = row[0][0]
    # 3. register player and tournament in tournament_contestants
    registerContestants(player_id, tournament_id)
    return player_id


def getTournamentID(tournament):
    """ Return's the tournament_id value from tournaments database when given the
        tournament's name as the parameter 'tournament'
        If no tournament exists of the name, returns a -1 to recognize this
    """
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
        query = "SELECT player_id, player_name, wins, matches from getMatchesAndWins where tournament_id = %s"
        values = (tourney[0],)
        rows = executeQuery(query, values)
        for row in rows:
            print('{0} {1} {2} {3}'.format(row[0], row[1], row[2], row[3]))
        standings.append(rows)
    if len(standings) > 1:
        # This is done for multiple tournaments
        return standings
    else:
        # In case of just one tournament, only one list is passed
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
    """ Returns player_id based on the player's name given by parameter 'name' """
    query = "select player_id from players where player_name = %s;"
    values = (name, )
    rows = executeQuery(query, values)
    if len(rows) > 0:
        return rows[0][0]
    else: return 'Not found'


def registerContestants(player, tournament):
    """ Registers the contestants per tournament
        Done for the case when multiple tournaments exist
    """
    value = str(player) + ', ' + str(tournament)
    query = "INSERT INTO tournament_contestants values (%s, %s);"
    values = (tournament, player, )
    executeQuery(query, values)


def swissPairings(tournament=None):
    """ Generate the swiss pairings for a given tournament. if tournament is not
        given, then creates swiss pairs out of the default tournament playerStandings
        Logic:
            1. get tournament_id and calculate total rounds and total matches possible
            2. for tournament_id, check if each player has played the same number of matches
            3. if each player has played the same number of matches, check if matches played = max
                if odd players, then total players = n+1 where n is registered players (so one player can get a bye)
                note:   total rounds = log(2) n         where n players
                        or           = log(2) (n+1)     where n players and n odd
                        total matches = (log(2) n) x n/2    where n players
                        or            = log(2) (n+1) x (n+1)/2 where n players and n odd
            4. if odd number of players, give a player a bye in that round
                (making sure only one bye per player per tournament)
            5. generate swiss pairing by sorting players by wins
    """
    # 1. get tournament_id and calculate total rounds and total matches possible
    player_pairs = []
    if tournament is not None:
        count_players = countPlayersInTournament(tournament)
        tournament_id = getTournamentID(tournament)
    else:
        count_players = countPlayersInTournament('Default')
        tournament_id = getTournamentID('Default')
    # check if count_players is odd, need to allocate a "space" for bye in that case
    print("We just measured players to be: {0}".format(count_players))
    if count_players<0:
        print("We don't have any players!")
    else:
        # increase count_players if odd number to make "space" for bye
        #if count_players%2 != 0:
        #    count_players += 1
        #else:
        #    pass

        total_rounds = round(math.log(count_players, 2))
        total_matches = round(total_rounds * count_players/2)
        print("Total Players: {0}, Rounds: {1}, matches {2}".format(count_players, total_rounds, total_matches))
        # 2. for tournament_id, check if each player has played the same number of matches
        query = "select getMatches.player_id, getMatches.matches from getMatches where getMatches.tournament_id = %s"
        values = (tournament_id, )
        match_info_rows = executeQuery(query, values)
        # Rows contains a list of tuples (player_id, matches played)
        # We first separate the matches played of all players into a list
        matches_played = [row[1] for row in match_info_rows]
        # Then we check if all the elements (matches played of all players) is the same
        all_played_same_matches = all(x == matches_played[0] for x in matches_played)
        if all_played_same_matches:
            # 3. if each player has played the same number of matches, check if matches played = max
            if matches_played[0] == total_matches:
                print("We have played all the matches possible in this Swiss Style Tournament")
            else:
                # get players ordered by wins
                query = "select getWins.player_id, players.player_name from getWins, players where players.player_id = getWins.player_id"
                players_by_wins_rows = executeQuery(query)
                # 4. if odd number of players, give a player a bye in that round
                #    (making sure only one bye per player per tournament)
                if len(players_by_wins_rows) %2 is not 0:
                    for player_count in range(0, len(players_by_wins_rows)):
                        query = "select * from bye_list where player_id = %s"
                        values = (players_by_wins_rows[player_count][0], )
                        bye_rows = executeQuery(query, values)
                        if len(bye_rows) == 0:
                            query = "insert into bye_list values (%s, %s)"
                            values = (tournament_id, players_by_wins_rows[player_count][0])
                            insert_bye_row = executeQuery(query, values)
                            bye_player = players_by_wins_rows.pop(player_count)
                            players_by_wins_rows.append(bye_player)
                            players_by_wins_rows.append((None, 'bye'))
                            break
                print(players_by_wins_rows)
                # 5. generate swiss pairing by sorting players by standing
                player_pairs = getPlayerPairs(players_by_wins_rows)
        else:
            print("We have players who still haven't played in this round...")
            for row in rows:
                print("Player ID: {0} has played {1} matches".format(row[0], row[1]))
    return player_pairs


def getPlayerPairs(players):
    """ Returns a list of tuples """
    # check if we need a bye, i.e if the number of players is odd
    players.reverse()
    player_pairs = []
    while len(players) > 0:
        player_pairs.append((players.pop() + players.pop()))
    return player_pairs

