-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


--  CREATE DATABASE swiss_style; Assuming the data base is already created
CREATE TABLE IF NOT EXISTS tournaments
(
    tournament_id       serial primary key,
    tournament_name     text
);

CREATE TABLE IF NOT EXISTS players
(
    player_id           serial primary key,
    player_name         text
);

CREATE TABLE IF NOT EXISTS tournament_contestants
(
    tournament_id       serial references tournaments ON DELETE CASCADE,
    player_id           serial references players ON DELETE CASCADE,
    player_points       integer DEFAULT 0,
    primary key (player_id, tournament_id)
);

CREATE TABLE IF NOT EXISTS swiss_pairs
(
    tournament_id       integer references tournaments ON DELETE CASCADE,
    match_id            serial UNIQUE,
    player1_id          integer,
    player2_id          integer,
    round               integer,
    winner_id           integer,
    primary key         (match_id, tournament_id),
    foreign key         (player1_id, tournament_id) references tournament_contestants ON DELETE CASCADE,
    foreign key         (player2_id, tournament_id) references tournament_contestants ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS match_list
(
    tournament_id          serial,
    match_id               serial,
    foreign key (match_id, tournament_id) references swiss_pairs ON DELETE CASCADE,
    player_id           serial references players ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS winners_list
(
    tournament_id          serial,
    match_id               serial,
    foreign key (match_id, tournament_id) references swiss_pairs ON DELETE CASCADE,
    winner_id          serial references players ON DELETE CASCADE
);

CREATE VIEW getWins AS
SELECT  tournament_contestants.tournament_id, tournament_contestants.player_id,
        count(swiss_pairs.match_id) AS wins
        FROM tournament_contestants left join swiss_pairs
        on tournament_contestants.player_id = swiss_pairs.winner_id
        and tournament_contestants.tournament_id = swiss_pairs.tournament_id
        group by tournament_contestants.tournament_id, tournament_contestants.player_id
        order by tournament_contestants.tournament_id;

CREATE VIEW getMatches AS
SELECT  tournament_contestants.tournament_id, tournament_contestants.player_id,
        count(match_list.match_id) as matches
        from tournament_contestants left join match_list
        on tournament_contestants.player_id = match_list.player_id
        and tournament_contestants.tournament_id = match_list.tournament_id
        group by tournament_contestants.tournament_id, tournament_contestants.player_id
        order by tournament_contestants.tournament_id;

CREATE VIEW getMatchesAndWins AS
SELECT  getMatches.tournament_id,
        getMatches.player_id,
        getMatches.matches,
        getWins.wins
        from getMatches, getWins
        where getMatches.tournament_id = getWins.tournament_id
        and getMatches.player_id = getWins.player_id;

CREATE VIEW getPlayersInfo AS
SELECT  tournament_contestants.tournament_id,
        players.player_id,
        players.player_name
        from tournament_contestants, players
        where tournament_contestants.player_id = players.player_id;


CREATE VIEW getPlayerStandings AS
SELECT  getPlayersInfo.tournament_id,
        getPlayersInfo.player_id,
        getPlayersInfo.player_name,
        getMatchesAndWins.matches,
        getMatchesAndWins.wins
        from getPlayersInfo, getMatchesAndWins
        where getPlayersInfo.tournament_id = getMatchesAndWins.tournament_id
        and getPlayersInfo.player_id = getMatchesAndWins.player_id
        order by tournament_id asc, wins desc;

CREATE VIEW getSwissPairs AS
select one.player1_id, one.player_name as player1_name, two.player2_id, two.player_name as player2_name
        from
        (select swiss_pairs.match_id, swiss_pairs.player1_id, players.player_name
                from swiss_pairs, players
                where swiss_pairs.player1_id = players.player_id
        ) as one,
        (select swiss_pairs.match_id, swiss_pairs.player2_id, players.player_name
                from swiss_pairs, players
                where swiss_pairs.player2_id = players.player_id
        ) as two
        where one.match_id = two.match_id;
