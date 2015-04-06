README

Project 2: Swiss Style Tournament

INTRODUCTION:

This project allows the user to create and run swiss style tournaments.
For more on swiss style tournaments - http://en.wikipedia.org/wiki/Swiss-system_tournament

We will use POSTGRESQL for our database requirements.


REQUIREMENTS:

To run this project, you will need the following files:

- tournament.py:
      collection of functions required to connect/execute queries from POSTGRES database
      collection of all the functions required to run a swiss style tournament

- tournament_test.py:
      collection of unit tests required to verify tournament.py

- tournament.sql:
      collection of POSTGRES table descriptions to create tables in the database
      collection of POSTGRES views to create views for presenting certain data

- tournament_delete.sql:
      collection of POSTGRES delete commands to delete all tables/views created in tournament.sql

Additional requirements are:
- Python 2.7.3
- psycopg2 module for python installed
- POSTGRESQL 9.3.6 installed


CONFIGURATION:

1. Download and install POSTGRESQL -
      http://www.postgresql.org/download/
2. Install the psycopg2 module for python -
      http://initd.org/psycopg/docs/install.html
3. To create database and import SQL schema for the Swiss Style Tournament
      application, open terminal and first navigate to where the files mentioned above in REQUIREMENTS are stored.
4. After navigating to the folder where the files are stored, type "psql" in
      the terminal to open POSTGRESQL.
5. Inside POSTGRESQL, type "\i tournament.sql". This will open the
      tournament.sql file (see above) which will create the database, required tables, and the views (which help with getting data from our tables).
      Note: if you forget step 3., POSTGRESQL will not be able to find the tournament.sql file (In this case, quit from POSTGRESQL by typing "\q" and navigate to the folder, before repeating step 4.).
6. Type "\q" to exit the POSTGRESQL application.


EXECUTING THE UNIT TESTS:

The file "tournament_test.py" has a set of unit tests that can help verify function of the swiss style tournament. All functions required to run the swiss style tournament are in the file "tournament.py".

1. Once you have configured the database for our swiss style tournament,
      you can return to the terminal and run the file tournament_test.py.
2. In terminal, once again navigate to where the files mentioned above in
      REQUIREMENTS are stored, and type "python tournament_test.py".
3. This will run the unit tests described in tournament_test.py.
4. You may want to reconfigure the database, in which case just follow the same steps as described in the "CONFIGURATION" section.




