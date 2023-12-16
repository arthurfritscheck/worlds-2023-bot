import discord
from discord.ext import commands, tasks
import datetime
import sqlite3
from database_operations import update_match_data
from discord import Component
from discord.ui import Button, View
import random

bot_token = 'insert_token_here'
 
intents = discord.Intents.all()
bot = commands.Bot(command_prefix= '!', case_insenstive=True, intents=intents)
components = Component()

# database connection
db_connection = sqlite3.connect('worldspredictions.db') # change the name of database if necessary
db_cursor = db_connection.cursor()
current_time_utc = datetime.datetime.utcnow()

matches_with_message_sent = set()

def load_matches():
    current_time_utc = datetime.datetime.utcnow()

    db_cursor.execute("SELECT * FROM matches WHERE DateTimeUTC >= ?", current_time_utc)
    return db_cursor.fetchall()

def upcoming_matches():
    # Query matches table
    current_time_utc = datetime.datetime.utcnow()

    db_cursor.execute("SELECT * FROM matches WHERE DateTime_UTC >= ? AND DateTime_UTC <= ?",
                      (current_time_utc, current_time_utc + datetime.timedelta(days=2)))
    return db_cursor.fetchall()

# function to retrieve individual match details based on match_id
def get_match_details(match_id):
    db_cursor.execute("SELECT * FROM matches WHERE MatchId = ?", (match_id,))
    match_details = db_cursor.fetchone()
    return match_details

async def button_callback(interaction):
    # process button click into variables
    user_id = interaction.user.id
    username = interaction.user.display_name
    username_mention = interaction.user.mention
    custom_id = interaction.data["custom_id"]
    custom_id_parts = custom_id.split("$")
    match_id = custom_id_parts[1]
    prediction = "-".join(custom_id_parts[2:])
    
    # data from matches table in sqlite database
    match_details = get_match_details(match_id)
    best_of = match_details[3]
    team1 = match_details[4]
    team2 = match_details[5]

    # time variables
    current_time_utc = datetime.datetime.utcnow()
    match_start_time_str = match_details[2]
    match_start_time = datetime.datetime.strptime(match_start_time_str, '%Y-%m-%d %H:%M:%S')

    predicted_team1_score = int(prediction.split("-")[0])
    predicted_team2_score = int(prediction.split("-")[1])


    if best_of == 5:
        predicted_winner = 1 if predicted_team1_score == 3 else 2
    elif best_of == 3:
        predicted_winner = 1 if predicted_team1_score == 2 else 2
    elif best_of == 1:
        predicted_winner = 1 if predicted_team1_score == 1 else 2

    if current_time_utc > match_start_time:
        await interaction.response.defer()
        await interaction.followup.send(f"This match has already started. Unfortunately, you cannot make or change your prediction anymore.")

    else:    
        # store the prediction
        db_cursor.execute("""
            INSERT INTO predictions (UserID, Username, MatchId, Tournament, DateTime_UTC, BestOf, Team1, Team2, PredictedWinner, PredictedTeam1Score, PredictedTeam2Score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(UserID, MatchId) DO UPDATE
            SET UserID = excluded.UserID, Username = excluded.Username, MatchId = excluded.MatchId, Tournament = excluded.Tournament, 
                DateTime_UTC = excluded.DateTime_UTC, BestOf = excluded.BestOf, Team1 = excluded.Team1, Team2 = excluded.Team2,
                PredictedWinner = excluded.PredictedWinner, PredictedTeam1Score = excluded.PredictedTeam1Score, PredictedTeam2Score = excluded.PredictedTeam2Score;
        """, (user_id, username, match_id, match_details[1], match_details[2], match_details[3],
            match_details[4], match_details[5], predicted_winner, predicted_team1_score, predicted_team2_score))
        db_connection.commit()

        await interaction.response.defer()
        await interaction.followup.send(f"{username_mention} prediction for Bo{best_of}  `{team1}-{team2}`: `{predicted_team1_score}-{predicted_team2_score}`")
        print(f"{username} prediction stored. Match type: Bo{best_of}. Matchup: {team1}-{team2}. MatchId: {match_id}. UserID: {user_id}.")

#async def send_prediction_message(match, ctx):
async def send_prediction_message(match):
    match_id, tournament, datetime_utc, best_of, team1, team2, winner, team1_score, team2_score = match 
    # Determine the number of buttons based on match type (Bo1, Bo3, Bo5)
    # use of "$" to ensure ease of string manipulation.
    
    bo1_button1_0 = (Button(label="1-0", style=discord.ButtonStyle.blurple, row=0, custom_id=f"predict${match_id}$1-0"))
    bo1_button0_1 = (Button(label="0-1", style=discord.ButtonStyle.red, row=1, custom_id=f"predict${match_id}$0-1"))

    bo3_button2_0 = (Button(label="2-0", style=discord.ButtonStyle.blurple, row=0, custom_id=f"predict${match_id}$2-0"))
    bo3_button2_1 = (Button(label="2-1", style=discord.ButtonStyle.blurple, row=0, custom_id=f"predict${match_id}$2-1"))
    bo3_button1_2 = (Button(label="1-2", style=discord.ButtonStyle.red, row=1, custom_id=f"predict${match_id}$1-2"))
    bo3_button0_2 = (Button(label="0-2", style=discord.ButtonStyle.red, row=1, custom_id=f"predict${match_id}$0-2"))

    bo5_button3_0 = (Button(label="3-0", style=discord.ButtonStyle.blurple, row=0, custom_id=f"predict${match_id}$3-0"))
    bo5_button3_1 = (Button(label="3-1", style=discord.ButtonStyle.blurple, row=0, custom_id=f"predict${match_id}$3-1"))
    bo5_button3_2 = (Button(label="3-2", style=discord.ButtonStyle.blurple, row=0, custom_id=f"predict${match_id}$3-2"))
    bo5_button0_3 = (Button(label="0-3", style=discord.ButtonStyle.red, row=1, custom_id=f"predict${match_id}$0-3"))
    bo5_button1_3 = (Button(label="1-3", style=discord.ButtonStyle.red, row=1, custom_id=f"predict${match_id}$1-3"))
    bo5_button2_3 = (Button(label="2-3", style=discord.ButtonStyle.red, row=1, custom_id=f"predict${match_id}$2-3"))
    
    view = View(timeout=None)

    if best_of == 1:
        view.add_item(bo1_button1_0)
        view.add_item(bo1_button0_1)
    elif best_of == 3:
        view.add_item(bo3_button2_0)
        view.add_item(bo3_button2_1)
        view.add_item(bo3_button1_2)
        view.add_item(bo3_button0_2)
    elif best_of == 5:
        view.add_item(bo5_button3_0)
        view.add_item(bo5_button3_1)
        view.add_item(bo5_button3_2)
        view.add_item(bo5_button0_3)
        view.add_item(bo5_button1_3)
        view.add_item(bo5_button2_3)
    
    for button in view.children:
        button.callback = button_callback

    # Send the message with buttons
    channel_id = 123456789 #insert channel_id of text channel you want prediction messages to be sent to
    channel = bot.get_channel(channel_id)
    await channel.send(f"Predict the best of {best_of} between {team1} and {team2}:", view=view)

@tasks.loop(hours=3) # Adjust the interval as needed
async def check_matches():
    upcoming_matches_list = upcoming_matches()
    for match in upcoming_matches_list:
        match_id = match[0]
        if match_id not in matches_with_message_sent:
            await send_prediction_message(match) # send prediction message
            matches_with_message_sent.add(match_id)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('--------------------------')
    check_matches.start()

@check_matches.before_loop
async def before_check_matches():
    await bot.wait_until_ready()

@bot.event
async def on_shutdown():
    print("Shutting down!")
    # Close the database connection when the bot is shutting down
    db_connection.close()

@bot.command()
async def all_commands(ctx):
    await ctx.send("""
List of commands:
!schedule
!score
!goat
!spaghetticode
""")

@bot.command()
async def spaghetticode(ctx):
    gif_url = "https://tenor.com/view/mario-spaghetti-italian-gif-14634187"
    await ctx.send(gif_url)

@bot.command()
async def goat(ctx):
    gif_url = 'https://tenor.com/view/gigashy-gif-13678897940992225847'
    await ctx.send(gif_url)

@bot.command()
async def schedule(ctx):
    url = 'https://lolesports.com/schedule?leagues=worlds,wqs'
    await ctx.send(url)

@bot.command()
async def score(ctx):
    user_scores = {}

    # Retrieve data from the Matches table
    db_cursor.execute("SELECT MatchId, BestOf, Winner, Team1Score, Team2Score FROM matches")
    matches_data = db_cursor.fetchall()

    # Retrieve data from the Predictions table and associate usernames
    db_cursor.execute("SELECT UserID, Username, MatchId, PredictedWinner, PredictedTeam1Score, PredictedTeam2Score FROM predictions")
    predictions_data = db_cursor.fetchall()

    for user_id, username, predicted_match_id, predicted_winner, predicted_team1_score, predicted_team2_score in predictions_data:
        for match_id, best_of, actual_winner, team1_score, team2_score in matches_data:
            if predicted_match_id == match_id:
                
                if actual_winner is not None and team1_score is not None and team2_score is not None:
                    if user_id not in user_scores:
                        user_scores[user_id] = {'username': username, 'score': 0} 
                    
                    if best_of == 1:
                        if predicted_winner == actual_winner:
                            user_scores[user_id]['score'] += 1
                    elif best_of == 3:
                        if predicted_winner == actual_winner and predicted_team1_score == team1_score and predicted_team2_score == team2_score:
                            user_scores[user_id]['score'] += 2
                        elif predicted_winner == actual_winner:
                            user_scores[user_id]['score'] += 1
                    elif best_of == 5:
                        if predicted_winner == actual_winner and predicted_team1_score == team1_score and predicted_team2_score == team2_score:
                            user_scores[user_id]['score'] += 3
                        elif predicted_winner == actual_winner:
                            user_scores[user_id]['score'] += 1    
    
    embed = discord.Embed(title="SCOREBOARD", color=0x00ff00)

    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    user_field = ""
    score_field = ""

    for user_id, data in sorted_scores:
        user_field += f"{data['username']}\n"
        score_field += f"{data['score']} points\n"
    
    
    embed.add_field(name="User", value=user_field, inline=True)
    embed.add_field(name="Score", value=score_field, inline=True)

    await ctx.send(embed=embed)

# in case the command used is not a valid command
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        
        await ctx.send("This is not a valid command. Use `!commands` to see the available commands")
    else:
        # Handle other types of command errors
        print(f"An error occurred: {error}")


bot.run(bot_token)

