#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    print("The standings are: {0}".format(standings))
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testMultipleTournaments():
    deleteTournaments()
    deleteMatches()
    deletePlayers()
    tid1 = registerTournament("Wimbledon")
    pid1 = registerPlayer("Pete Sampras", "Wimbledon")
    pid2 = registerPlayer("Andre Agassi", "Wimbledon")
    tid2 = registerTournament("US Open")
    registerContestants(pid1, tid2)
    registerContestants(pid2, tid2)
    pid3 = registerPlayer("Roger Federer", "Wimbledon")
    count_in_tour1 = countPlayersInTournament("Wimbledon")
    count_in_tour2 = countPlayersInTournament("US Open")
    if count_in_tour1 != 3 and count_in_tour2 != 2:
        raise ValueError(
            "First tournament should have 3 players, second tournament 2 players.")
    print "9. Correct number of players in both tournaments"



def testCompleteSwissPairing():
    deleteMatches()
    deletePlayers()
    registerPlayer("Don Draper")
    registerPlayer("Roger Sterling")
    registerPlayer("Peggy Olson")
    registerPlayer("Joan Holloway")
    autoSwissPairing()
    standings = playerStandings()
    [name1, name2, name3, name4] = [row[1] for row in standings]
    expected_names_order = ["Don Draper", "Roger Sterling", "Peggy Olson", "Joan Holloway"]
    actual_names_order = [name1, name2, name3, name4]
    if expected_names_order != actual_names_order:
        raise ValueError(
            "After one entire tournament's swiss pairing with even players, player standings order is incorrect.")
    print "10. After one entire tournament's swiss pairing with even players, correct player standings."


def autoSwissPairing():
    pairings = [1]  #default so we can have atleast one round
    swiss_round = 1
    while len(pairings) > 0:
        print("Round: {0}".format(swiss_round))
        print("Standings: ")
        playerStandings()
        pairings = swissPairings()
        print(pairings)
        for pair in pairings:
            if pair[0] is None:
                winner_id = pair[2]
                loser_id = -1
                print("Bye for player: {0}".format(pair[3]))
            elif pair[2] is None:
                winner_id = pair[0]
                loser_id = -1
                print("Bye for player: {0}".format(pair[1]))
            else:
                winner_id = pair[0]
                loser_id = pair[2]
                print("Winner of {0} and {1} is: {2}".format(pair[1], pair[3], pair[1]))
            reportMatch(winner_id, loser_id)
        swiss_round += 1
    return pairings


def testBye():
    deleteMatches()
    deletePlayers()
    # test for odd number of players
    registerPlayer("Don Draper")
    registerPlayer("Roger Sterling")
    registerPlayer("Peggy Olson")
    registerPlayer("Joan Holloway")
    registerPlayer("Pete Campbell")
    pairings = autoSwissPairing()
    standings = playerStandings()
    [name1, name2, name3, name4, name5] = [row[1] for row in standings]
    expected_names_order = ["Don Draper", "Joan Holloway", "Peggy Olson", "Roger Sterling", "Pete Campbell"]
    actual_names_order = [name1, name2, name3, name4, name5]
    if expected_names_order != actual_names_order:
        raise ValueError(
            "After one entire tournament with odd players, player standings order is incorrect.")
    print "11. After one entire tournament with odd players, correct player standings."


def testTiedMatch():
    deleteMatches()
    deletePlayers()
    id1 = registerPlayer("Robert Plant")
    id2 = registerPlayer("Jimmy Page")
    id3 = registerPlayer("John Paul Jones")
    id4 = registerPlayer("John Bonham")
    reportMatch(id1, id2, 1)
    reportMatch(id3, id4)
    standings = playerStandings()
    expected_standings = [id3, id1, id2, id4]
    actual_standings = [standings[0][0], standings[1][0], standings[2][0], standings[3][0]]
    if actual_standings!=expected_standings:
        raise ValueError(
            "Tied games should count for more than lost games, but less than won games.")
    print "12. With one tied game, the standings are correct."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()

    #Extra credit - assuming any number of players (odd or even)
    testMultipleTournaments()
    testCompleteSwissPairing()
    testBye()
    testTiedMatch()
    print "Success!  All tests pass!"


