# worlds-2023-bot
A discord bot that uses match data from Leaguepedia's API to allow users to predict the outcome of League of Legends matches, in this case the Worlds 2023 tournament. The reason I built this bot is because in my friend group, we like to see who can best predict the outcome of all of the matches. In past years, we had to manually do the entire process of sending out the messages, predicting the games, saving the predictions and calculating the score of each user. By making this bot, this process is almost completely automated, which makes the whole process of running such a competition a lot smoother. 

# How it is made
Tech used: Python, Sqlite3
The bot is written in Python, with sqlite3 used for all data purposes such as fetching the data as well as storing the predictions in the database. The bot fetches the updated match data from the Leaguepedia API, which then is stored in a local database. Once the data is updated, the bot will send out a seperate message for each match that will start in less than 24 hours (this can be adjusted to any desired timeframe). The predictions are then stored in another table in the same database. Scores are based on the unique match_id of each match, as well as each unique discord user_id, to ensure every match and predictions is unique. 

# Lessons Learned
This being my first self-thought of project, there were many lessons I can take away that I learned from building this bot. This was my first time working with API's, as well as the first time seeing my code with others, which came with many challenges. Once the bot was finally deployed and working as intented, it was awesome to see
