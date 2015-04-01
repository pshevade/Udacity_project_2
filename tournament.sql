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
    winner_id               integer,
    loser_id                integer,
    primary key (match_id, tournament_id)
);

CREATE TABLE IF NOT EXISTS swiss_pairs
(
    tournament_id       integer references tournaments ON DELETE CASCADE,
    match_id            integer,
    player1_id          integer,
    player2_id          integer,
    round               integer,
    foreign key         (match_id, tournament_id) references match_list ON DELETE CASCADE,
    foreign key         (player1_id, tournament_id) references tournament_contestants ON DELETE CASCADE,
    foreign key         (player2_id, tournament_id) references tournament_contestants ON DELETE CASCADE
);



CREATE VIEW getWins AS
    SELECT  tournament_contestants.tournament_id,
            tournament_contestants.player_id,
            count(match_list.winner_id) as wins
            from tournament_contestants left join match_list
            on tournament_contestants.player_id = match_list.winner_id
            and tournament_contestants.tournament_id = match_list.tournament_id
            group by tournament_contestants.tournament_id,
            tournament_contestants.player_id
            order by  wins desc;

CREATE VIEW getMatches AS
    SELECT  tournament_contestants.tournament_id,
            tournament_contestants.player_id,
            count(match_list.match_id) as matches
            from tournament_contestants left join match_list
            on tournament_contestants.player_id = match_list.winner_id
            and tournament_contestants.tournament_id = match_list.tournament_id
            or tournament_contestants.player_id = match_list.loser_id
            and tournament_contestants.tournament_id = match_list.tournament_id
            group by tournament_contestants.tournament_id,
            tournament_contestants.player_id
            order by matches desc;

CREATE VIEW getMatchesAndWins AS
    SELECT  tournament_contestants.tournament_id,
            players.player_id,
            players.player_name,
            getWins.wins,
            getMatches.matches
            from tournament_contestants, players, getWins, getMatches
            where   tournament_contestants.tournament_id = getWins.tournament_id
            and     tournament_contestants.tournament_id = getMatches.tournament_id
            and     tournament_contestants.player_id = players.player_id
            and     tournament_contestants.player_id = getWins.player_id
            and     tournament_contestants.player_id = getMatches.player_id
            order by getWins.wins desc;


