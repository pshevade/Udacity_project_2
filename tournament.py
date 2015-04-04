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


def deleteTournaments():
    """Remove all tournaments from database """
    query = "DELETE FROM tournaments"
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
    tournament_id = getTournamentID(tournament)
    query = "SELECT count(*) from tournament_contestants where tournament_id = %s"
    values = (tournament_id, )
    rows = executeQuery(query, values)
    return rows[0][0]


def registerPlayer(name, tournament="Default"):
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
    tournament_id = getTournamentID(tournament)
    if tournament_id == -1:
        tournament_id = registerTournament(tournament)
    '''if tournament is not None:
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
    '''
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
        print("No tournament exits, may need to create tournament {0}".format(tournament))
        tournament_id = -1
    return tournament_id


def playerStandings(tournament="Default"):
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
    tournament_id = getTournamentID(tournament)
    standings = []
    #query = "SELECT player_id, player_name, wins, matches from getMatchesAndWins where tournament_id = %s"
    # Check if any players are tied by points
    query = "SELECT a.player_id, b.player_id from getMatchesAndWins as a, getMatchesAndWins as b where a.player_points = b.player_points and a.player_id < b.player_id order by a.player_points"
    tied_players_rows = executeQuery(query)

    print("The tied pairs are: {0}".format(tied_players_rows))
    reordered_rows = []
    for tied_players in tied_players_rows:
        tied_players = resolveOMW(tied_players[0], tied_players[1])
        reordered_rows.append(tied_players)
        print("The tied players are ordered as: {0}".format(tied_players))

    print("The tied players row is now as: {0}".format(reordered_rows))

    query = "SELECT player_id, player_name, wins, matches, player_points from getMatchesAndWins where tournament_id = %s"
    values = (tournament_id,)
    standings_rows = executeQuery(query, values)
    print("Before OMW:")
    for row in standings_rows:
        print('{0} {1} {2} {3} {4}'.format(row[0], row[1], row[2], row[3], row[4]))

    for tied_pair in reordered_rows:
        for standings in standings_rows:
            if tied_pair[0] == standings[0]:
                index_p1 = standings_rows.index(standings)
            if tied_pair[1] == standings[0]:
                index_p2 = standings_rows.index(standings)
        if index_p1 > index_p2:
            standings_rows[index_p1], standings_rows[index_p2] = standings_rows[index_p2], standings_rows[index_p1]
    print("After OMW resolved: ")
    player_standings = []
    for row in standings_rows:
        print('{0} {1} {2} {3} {4}'.format(row[0], row[1], row[2], row[3], row[4]))
        player_standings.append((row[0], row[1], row[2], row[3]))
    print("Standings' length is: {0}".format(len(player_standings)))
    return player_standings


def reportMatch(winner, loser, tied=0, tournament="Default"):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    tournament_id = getTournamentID(tournament)
    if tied == 0:
        values_report_match = (tournament_id, winner, loser, winner, tied)
        query2 = "UPDATE tournament_contestants set player_points = player_points + 2 where player_id = %s"
        values2 = (winner,)
        executeQuery(query2, values2)
    else:
        values_report_match = (tournament_id, winner, loser, -1, tied)
        query2 = "UPDATE tournament_contestants set player_points = player_points + 1 where player_id = %s"
        values2 = (winner,)
        executeQuery(query2, values2)
        values2 = (loser,)
        executeQuery(query2, values2)
    query_report_match = "INSERT into match_list (tournament_id, player1_id, player2_id, winner_id, tied) values (%s, %s, %s, %s, %s)"
    rows = executeQuery(query_report_match, values_report_match)


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
    query = "INSERT INTO tournament_contestants values (%s, %s);"
    values = (tournament, player, )
    executeQuery(query, values)


def swissPairings(tournament="Default"):
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
    count_players = countPlayersInTournament(tournament)
    tournament_id = getTournamentID(tournament)
    # check if count_players is odd, need to allocate a "space" for bye in that case
    print("We just measured players to be: {0}".format(count_players))
    if count_players<0:
        print("We don't have any players!")
    else:
        total_rounds = round(math.log(count_players, 2))
        total_matches = round(total_rounds * count_players/2)
        print("Total Players: {0}, Rounds: {1}, matches {2}".format(count_players, total_rounds, total_matches))
        # 2. for tournament_id, check if each player has played the same number of matches
        standings = playerStandings(tournament)
        # We get player_id, player_name, matches_played, wins
        # Rows contains a list of tuples (player_id, matches played)
        # We first separate the matches played of all players into a list
        matches_played = [row[3] for row in standings]
        # Then we check if all the elements (matches played of all players) is the same
        all_played_same_matches = all(x == matches_played[0] for x in matches_played)
        if all_played_same_matches:
            # 3. if each player has played the same number of matches, check if matches played = max
            if matches_played[0] == total_matches:
                print("We have played all the matches possible in this Swiss Style Tournament")
            else:
                # 4. if odd number of players, give a player a bye in that round
                #    (making sure only one bye per player per tournament)
                players_by_wins_bye = giveBye(standings, tournament_id)
                # 5. generate swiss pairing by sorting players by their standings/bye
                player_pairs = getPlayerPairs(players_by_wins_bye)
        else:
            print("We have players who still haven't played in this round...")
            for row in rows:
                print("Player ID: {0} has played {1} matches".format(row[0], row[1]))
    return player_pairs


def giveBye(standings, tournament_id):
    """ In case of making swiss pairs for an odd number of players in
        the tournament, one player needs to be given a bye.
        This function figures out which player hasn't been given a bye yet,
        and gives that player a bye
        The list of players with a bye is stored in the database.
        Only one bye per player per tournament
    """
    # get players by the player_id (0th element) & their wins (2nd element)
    players_by_wins_rows = [(row[0], row[2]) for row in standings]
    # Only need to give a bye in case there are odd number of players
    if len(players_by_wins_rows) %2 is not 0:

        for player_count in range(0, len(players_by_wins_rows)):
            query = "select * from bye_list where player_id = %s and tournament_id = %s"
            values = (players_by_wins_rows[player_count][0], tournament_id, )
            bye_rows = executeQuery(query, values)
            if len(bye_rows) == 0:
                query = "insert into bye_list values (%s, %s)"
                values = (tournament_id, players_by_wins_rows[player_count][0])
                insert_bye_row = executeQuery(query, values)
                bye_player = players_by_wins_rows.pop(player_count)
                players_by_wins_rows.append(bye_player)
                players_by_wins_rows.append((None, 'bye'))
                break

    return players_by_wins_rows


def getPlayerPairs(players):
    """ Returns a list of tuples """
    # check if we need a bye, i.e if the number of players is odd
    players.reverse()
    player_pairs = []
    while len(players) > 0:
        player_pairs.append((players.pop() + players.pop()))
    return player_pairs


def resolveOMW(player1, player2, tournament="Default"):
    """ Logic:
            1. get all players player1 has played with
            2. get all players player2 has played with
            3. get list of common players
            4. for player1, calculate all the players from common list they have won against
            5. for player2, calculate all the players from common list they have won against
            6. return players based on who won against most common opponents
    """
    tournament_id = getTournamentID(tournament)
    query = "SELECT player2_id from match_list where player1_id = %s and tournament_id = %s"
    values = (player1, tournament_id, )
    rows = executeQuery(query, values)
    print("returned rows: {0}".format(rows))
    players_p1_played_with = [row[0] for row in rows]

    query = "SELECT player1_id from match_list where player2_id = %s and tournament_id = %s"
    values = (player1, tournament_id, )
    rows = executeQuery(query, values)
    print("returned rows: {0}".format(rows))
    players_p1_played_with+= [row[0] for row in rows]

    query = "SELECT player2_id from match_list where player1_id = %s and tournament_id = %s"
    values = (player2, tournament_id, )
    rows = executeQuery(query, values)
    print("returned rows: {0}".format(rows))
    players_p2_played_with = [row[0] for row in rows]

    query = "SELECT player1_id from match_list where player2_id = %s and tournament_id = %s"
    values = (player2, tournament_id, )
    rows = executeQuery(query, values)
    print("returned rows: {0}".format(rows))
    players_p2_played_with+=[row[0] for row in rows]

    print("List of player ids player {0} played with: {1}".format(player1, players_p1_played_with))
    print("List of player ids player {0} played with: {1}".format(player2, players_p2_played_with))
    common_players_list = list(frozenset(players_p1_played_with).intersection(players_p2_played_with))
    print("List of common players: {0}".format(common_players_list))
    common_players_list.append(player1)
    common_players_list.append(player2)
    player1_vs_common_matches = []
    player2_vs_common_matches = []
    for common_player in common_players_list:
        query = "SELECT winner_id from match_list where player1_id = %s and player2_id = %s or player2_id = %s and player1_id = %s"
        values = (player1, common_player, player1, common_player,)
        rows = executeQuery(query, values)
        player1_vs_common_matches += [row[0] for row in rows]
        values = (player2, common_player, player2, common_player,)
        rows = executeQuery(query, values)
        player2_vs_common_matches += [row[0] for row in rows]

    print("Player 1 and common matches winners are: {0}".format(player1_vs_common_matches))
    print("Player 2 and common matches winners are: {0}".format(player2_vs_common_matches))
    matches_p1_won_against_common = player1_vs_common_matches.count(player1)
    matches_p2_won_against_common = player2_vs_common_matches.count(player2)
    print("Matches {0} won against common: {1}".format(player1, matches_p1_won_against_common))
    print("Matches {0} won against common: {1}".format(player2, matches_p2_won_against_common))

    if matches_p1_won_against_common > matches_p2_won_against_common:
        return (player1, player2)
    elif matches_p1_won_against_common < matches_p2_won_against_common:
        return (player2, player1)
    else:
        return (player1, player2)
    '''elif matches_p1_won_against_common == matches_p2_won_against_common:
        query = "SELECT winner_id from match_list where player1_id = %s and player2_id = %s or player2_id = %s and player1_id = %s"
        values = (player1, player2, player1, player2,)
        rows = executeQuery(query, values)
        if len(row) == 0:
            print("Players have won the same number of matches against opponents, and haven't played each other yet")
        else:
            if rows[0][0] == player1:
                return (player1, player2)
            elif rows[0][0]
    '''
