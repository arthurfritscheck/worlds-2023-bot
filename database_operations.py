import sqlite3
from mwrogue.esports_client import EsportsClient
import datetime 

def update_match_data():
    try:

        site = EsportsClient("lol")

        tournament_names = ["Worlds Qualifying Series 2023", 'Worlds 2023 Play-In', 'Worlds 2023 Main Event']
        tournament_names_query_list = ', '.join([f"'{name}'" for name in tournament_names])

        current_utc_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        database = 'worldspredictions.db'
        # Connect to the database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        # Query for series outcomes
        response = site.cargo_client.query(
            tables="MatchSchedule=MS, Tournaments=T",
            join_on="MS.OverviewPage=T.OverviewPage",
            fields="MS.MatchId, T.Name, MS.DateTime_UTC, MS.BestOf, MS.Team1, MS.Team2, MS.Winner, MS.Team1Score, MS.Team2Score",
            where=f"T.Name IN ({tournament_names_query_list})",
            limit=500
        )

        # Loop through the response data
        for record in response:
            match_id = record['MatchId']
            tournament_name = record['Name']
            date_time_utc = record['DateTime UTC']
            best_of = record['BestOf']
            team1 = record['Team1']
            team2 = record['Team2']
            winner = record['Winner']
            team1_score = record['Team1Score']
            team2_score = record['Team2Score']
                
            #print(f"Processing Match: {match_id}")

            # Check if the match already exists in the database
            cursor.execute("SELECT * FROM matches WHERE MatchId=?", (match_id,))
            existing_match = cursor.fetchone()

            if existing_match:
                # Update the existing record
                cursor.execute("UPDATE matches SET Team1=?, Team2=?, Winner=?, Team1Score=?, Team2Score=? WHERE MatchId=?", (team1, team2, winner, team1_score, team2_score, match_id))
                print(f"Updated match: {team1}-{team2}. MatchId: {match_id}")
            else:
                # Insert a new record
                cursor.execute("INSERT INTO matches (MatchId, Tournament, DateTime_UTC, BestOf, Team1, Team2, Winner, Team1Score, Team2Score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (match_id, tournament_name, date_time_utc, best_of, team1, team2, winner, team1_score, team2_score))
                print(f"Inserted new match: {match_id}")
        # Commit the changes
        
        conn.commit()

    
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to update match data
update_match_data()


