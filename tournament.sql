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
    player_name         text,
    player_points       integer
);

CREATE TABLE IF NOT EXISTS tournament_contestants
(
    tournament_id       serial references tournaments ON DELETE CASCADE,
    player_id           serial references players ON DELETE CASCADE,
    primary key (player_id, tournament_id)
);

CREATE TABLE IF NOT EXISTS swiss_pairs
(
    tournament_id       integer references tournaments ON DELETE CASCADE,
    match_id            serial UNIQUE,
    player1_id          integer,
    player2_id          integer,
    round               integer,
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
    winners_id          serial references players ON DELETE CASCADE
);
