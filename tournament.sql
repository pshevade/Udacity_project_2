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

CREATE TABLE IF NOT EXISTS match_list
(
    tournament_id          integer references tournaments ON DELETE CASCADE,
    match_id               serial UNIQUE,
    player1_id              integer,
    player2_id              integer,
    winner_id               integer,
    tied                     integer,
    primary key (match_id, tournament_id)
);

CREATE TABLE IF NOT EXISTS swiss_pairs
(
    tournament_id       integer references tournaments ON DELETE CASCADE,
    player1_id          integer,
    player2_id          integer,
    round               integer,
    foreign key         (player1_id, tournament_id) references tournament_contestants ON DELETE CASCADE,
    foreign key         (player2_id, tournament_id) references tournament_contestants ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bye_list
(
    tournament_id       integer references tournaments ON DELETE CASCADE,
    player_id           integer
);


CREATE VIEW getWins AS
    SELECT  tournament_contestants.tournament_id,
            tournament_contestants.player_id,
            tournament_contestants.player_points,
            count(match_list.winner_id) as wins
            from tournament_contestants left join match_list
            on tournament_contestants.player_id = match_list.winner_id
            and tournament_contestants.tournament_id = match_list.tournament_id
            group by tournament_contestants.tournament_id,
            tournament_contestants.player_id, tournament_contestants.player_points
            order by  wins desc, tournament_contestants.player_points desc,
            tournament_contestants.tournament_id asc,
            tournament_contestants.player_id asc;

CREATE VIEW getMatches AS
    SELECT  tournament_contestants.tournament_id,
            tournament_contestants.player_id,
            count(match_list.match_id) as matches
            from tournament_contestants left join match_list
            on tournament_contestants.player_id = match_list.player1_id
            and tournament_contestants.tournament_id = match_list.tournament_id
            or tournament_contestants.player_id = match_list.player2_id
            and tournament_contestants.tournament_id = match_list.tournament_id
            group by tournament_contestants.tournament_id,
            tournament_contestants.player_id
            order by matches desc;

CREATE VIEW getMatchesAndWins AS
    SELECT  tournament_contestants.tournament_id,
            players.player_id,
            players.player_name,
            getWins.wins,
            getWins.player_points,
            getMatches.matches
            from tournament_contestants, players, getWins, getMatches
            where   tournament_contestants.tournament_id = getWins.tournament_id
            and     tournament_contestants.tournament_id = getMatches.tournament_id
            and     tournament_contestants.player_id = players.player_id
            and     tournament_contestants.player_id = getWins.player_id
            and     tournament_contestants.player_id = getMatches.player_id
            order by getWins.wins desc, getWins.player_points desc, tournament_contestants.tournament_id asc,
            players.player_id asc;


