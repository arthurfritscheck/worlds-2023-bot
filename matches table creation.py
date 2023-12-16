import sqlite3

# Replace 'worldspredictions.db' with the desired database file name if necessary
database_file = 'worldspredictions.db'

# Connect to the SQLite database (this will create the database file if it doesn't exist)
conn = sqlite3.connect(database_file)
cursor = conn.cursor()



# Execute the SQL command to create the table
cursor.execute('''
    CREATE TABLE matches (
        MatchId TEXT PRIMARY KEY,
        Tournament TEXT,
        DateTime_UTC DATETIME,
        BestOf INTEGER,
        Team1 TEXT,
        Team2 TEXT,
        Winner INTEGER,
        Team1Score INTEGER,
        Team2Score INTEGER
    );            
''')

# Commit the changes and close the database connection
conn.commit()
conn.close()
