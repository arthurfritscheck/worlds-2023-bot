import sqlite3

# Connect to the SQLite database (it creates one if it does not exist yet)
db_connection = sqlite3.connect('worldspredictions.db')

# Create a cursor object to execute SQL commands
cursor = db_connection.cursor()

# Define the SQL statement to create the predictions table with a composite primary key
create_table_statement = """
CREATE TABLE predictions (
    UserID INTEGER,
    Username TEXT,
    MatchId TEXT,
    Tournament TEXT,
    DateTime_UTC DATETIME,
    BestOf INTEGER,
    Team1 TEXT,
    Team2 TEXT,
    PredictedWinner INTEGER,
    PredictedTeam1Score INTEGER,
    PredictedTeam2Score INTEGER,
    PRIMARY KEY (UserID, MatchId)
);
"""

# Execute the SQL statement to create the table
cursor.execute(create_table_statement)

# Commit the changes and close the database connection
db_connection.commit()
db_connection.close()
