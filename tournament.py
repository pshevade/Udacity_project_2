#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random
import math
import bleach

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    DB = psycopg2.connect("dbname=swiss_style")
    return DB, DB.cursor()


def executeQuery(query, values=None):
    """ Connect to database and execute the query that is passed
        Parameter 'values' can be a list of n elements, or can be None,
        in which case the query is fully described as is
    """
    rows = ['empty']
    DB_connection, cur = connect()
    if values is not None:
        cur.execute(query, values)
    else:
        cur.execute(query)
    DB_connection.commit()
    try:
        rows = cur.fetchall()
    except psycopg2.ProgrammingError:
        pass
    DB_connection.close()
    return rows


def registerTournament(name):
    """ Register a tournament, of the name give by parameter 'name'"""
    bleach.clean(name)

    query = "INSERT INTO tournaments (tournament_name) values (%s) RETURNING tournament_id;"
    values = (name,)
    row = executeQuery(query, values)
    return row[0][0]            # row will only have one element, the tournament_id


def deleteMatches():
    """ Remove all the match records from the database."""
    query = "DELETE FROM swiss_pairs"
    executeQuery(query)
    query = "DELETE FROM match_list"
    executeQuery(query)
    query = "DELETE FROM bye_list"
    executeQuery(query)


def deleteTournaments():
    """ Remove all tournaments from database """
    query = "DELETE FROM tournaments"
    executeQuery(query)


def deletePlayers():
    """ Remove all the player records from the database."""
    sub_query = "SELECT player_id from players"
    rows = executeQuery(sub_query)
    for row in rows:
        deleteSpecificPlayer(row[0])


def deleteSpecificPlayer(player_id):
    """ Deletes a specific player, based on the player_id"""
    query = "DELETE FROM players where player_id = %s"
    values = (player_id, )
    executeQuery(query, values)


def countPlayers():
    """ Count all players, across all tournaments
        Returns the number of players currently registered."""
    query = "SELECT count(*) from players;"
    row = executeQuery(query)
    return row[0][0]


def countPlayersInTournament(tournament):
    """ Count all players in a given tournament"""
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(tournament)

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
            1b. if tournament doesn't exist, create it
            2. register players
            3. register player and tournament in tournament_contestants
    """
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(name)
    bleach.clean(tournament)
    # 1. check if tournament exists:
    tournament_id = getTournamentID(tournament)
    # 1b. if tournament does not exist, register/create it
    if tournament_id == -1:
        tournament_id = registerTournament(tournament)
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
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(tournament)
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
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(tournament)

    tournament_id = getTournamentID(tournament)
    standings = []

    # Find the players are tied by points
    query = "SELECT a.player_id, b.player_id from getMatchesAndWins as a, getMatchesAndWins as b where a.player_points = b.player_points and a.player_id < b.player_id order by a.player_points"
    tied_players_rows = executeQuery(query)

    # Resolve them based on OMW.
    reordered_rows = []
    for tied_players in tied_players_rows:
        tied_players = resolveOMW(tied_players[0], tied_players[1])
        reordered_rows.append(tied_players)

    # Get the player standings ranked by wins and player_points
    query = "SELECT player_id, player_name, wins, matches, player_points from getMatchesAndWins where tournament_id = %s"
    values = (tournament_id,)
    standings_rows = executeQuery(query, values)

    # Rearrange the standings based on the tied pairs that need to be reordered based on OMW
    for tied_pair in reordered_rows:
        # Find the index where the player_id in tied_pair is in standings
        for standings in standings_rows:
            if tied_pair[0] == standings[0]:
                index_p1 = standings_rows.index(standings)
            if tied_pair[1] == standings[0]:
                index_p2 = standings_rows.index(standings)
        # Swap the rows in case they are incorrectly ordered based on OMW
        if index_p1 > index_p2:
            standings_rows[index_p1], standings_rows[index_p2] = standings_rows[index_p2], standings_rows[index_p1]

    # We only need player_id, player_name, wins, matches to return
    player_standings = []
    for row in standings_rows:
        player_standings.append((row[0], row[1], row[2], row[3]))
    return player_standings


def printStandings(standings):
    print("Player ID".ljust(10)+"Player Name".ljust(20)+"Wins".ljust(10)+"Matches".ljust(10))
    for row in standings:
        print(str(row[0]).ljust(10)+str(row[1]).ljust(20)+str(row[2]).ljust(10)+str(row[3]).ljust(10))


def reportMatch(winner, loser, tied=0, tournament="Default"):

    """Records the outcome of a single match between two players.

    Args:
      winner:   the id number of the player who won
      loser:    the id number of the player who lost
      tied:     in case the match is a tie, then winner, loser are just tied players
      tournament: defaults to "Default", this will allow to report matches per tournament name
    """
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(tournament)
    bleach.clean(winner)
    bleach.clean(loser)
    bleach.clean(tied)

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
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(name)

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
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(player)
    bleach.clean(tournament)

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
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(tournament)

    # 1. get tournament_id and calculate total rounds and total matches possible
    player_pairs = []
    count_players = countPlayersInTournament(tournament)
    tournament_id = getTournamentID(tournament)
    # check if count_players is odd, need to allocate a "space" for bye in that case
    if count_players<0:
        print("We don't have any players!")
    else:
        total_rounds = round(math.log(count_players, 2))
        total_matches = round(total_rounds * count_players/2)
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
                query = "INSERT into swiss_pairs values (%s, %s, %s, %s)"
                # The current round number is calculated by 2 ^ (matches played/total players/2)
                for pair in player_pairs:
                    values = (tournament_id, pair[0], pair[2], 2**round(matches_played[0]/(count_players/2)),)
                    executeQuery(query, values)
        else:
            print("We have players who still haven't played in this round, as follows: ")
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
    players_by_wins_rows = [(row[0], row[1]) for row in standings]
    # Only need to give a bye in case there are odd number of players
    if len(players_by_wins_rows) %2 is not 0:

        for player_count in range(0, len(players_by_wins_rows)):
            # Check if player has already been given a bye
            query = "select * from bye_list where player_id = %s and tournament_id = %s"
            values = (players_by_wins_rows[player_count][0], tournament_id, )
            bye_rows = executeQuery(query, values)
            # if bye has NOT been given to the player yet, bye_rows will be empty
            if len(bye_rows) == 0:
                # if player hasn't gotten a bye, give a bye, and insert this record
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
    """ Input:
        player1 : player's id
        player2 : player's id
        player1 and player 2 are ordered
        (i.e. if player of id 7 is ranked above id 3, player1 = 7, player2 = 3)

        Logic:
        1. get all players player1 has played with
        2. get all players player2 has played with
        3. make a list of players both players have played with
        4. add both players themselves to the list of common players
          - this is done to make sure we find out who won the match(es) between those
            two players as well as for player2,
            calculate all the players from common list they have won against
        5. Find out who won matches between player 1 and common list, and then
                                    between player 2 and common list
        6. See how many games against common opponents has player1 won and player2 won
        7. if player 2 has won more games than player 1, swap their order

    """
    # Sanitize input, in case it comes from web app/environment
    bleach.clean(tournament)

    # 1. get all players player1 has played with
    tournament_id = getTournamentID(tournament)
    query = "SELECT player2_id from match_list where player1_id = %s and tournament_id = %s"
    values = (player1, tournament_id, )
    rows = executeQuery(query, values)
    players_p1_played_with = [row[0] for row in rows]

    query = "SELECT player1_id from match_list where player2_id = %s and tournament_id = %s"
    values = (player1, tournament_id, )
    rows = executeQuery(query, values)
    players_p1_played_with+= [row[0] for row in rows]

    # 2. get all players player2 has played with
    query = "SELECT player2_id from match_list where player1_id = %s and tournament_id = %s"
    values = (player2, tournament_id, )
    rows = executeQuery(query, values)
    players_p2_played_with = [row[0] for row in rows]

    query = "SELECT player1_id from match_list where player2_id = %s and tournament_id = %s"
    values = (player2, tournament_id, )
    rows = executeQuery(query, values)
    players_p2_played_with+=[row[0] for row in rows]

    # 3. make a list of players both players have played with
    common_players_list = list(frozenset(players_p1_played_with).intersection(players_p2_played_with))

    # 4. add both players themselves to the list of common players
    #    - this is done to make sure we find out who won the match(es) between those
    #      two players as well
    common_players_list.append(player1)
    common_players_list.append(player2)

    # 5. Find out who won matches between player 1 and common list, and then
    #                             between player 2 and common list
    player1_vs_common_matches = []  # contains the winner id between player1 and corresponding common player
    player2_vs_common_matches = []  # contains the winner id between player2 and corresponding common player
    for common_player in common_players_list:
        query = "SELECT winner_id from match_list where player1_id = %s and player2_id = %s" \
                "or player2_id = %s and player1_id = %s"
        values = (player1, common_player, player1, common_player,)
        rows = executeQuery(query, values)
        player1_vs_common_matches += [row[0] for row in rows]
        values = (player2, common_player, player2, common_player,)
        rows = executeQuery(query, values)
        player2_vs_common_matches += [row[0] for row in rows]

    # 6. See how many games against common opponents has player1 won and player2 won
    #    From the list of winner_ids for matches between player1 and
    #    common list (and player2 and common list), we count how often winner_id = player1_id
    #    and how often winner_id = player2_id
    matches_p1_won_against_common = player1_vs_common_matches.count(player1)
    matches_p2_won_against_common = player2_vs_common_matches.count(player2)

    # 7. if player 2 has won more games than player 1, swap their order
    if matches_p1_won_against_common < matches_p2_won_against_common:
        return (player2, player1)
    else:
        return (player1, player2)
