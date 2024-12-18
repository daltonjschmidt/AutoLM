from pprint import pprint
import pandas as pd
from datetime import date
import sleeper
import postgres
import psycopg2
import json

#Global Variables
#Leagues to get data from (league number, year)
leagues = {'920151115868565504': 2023,'784647533929566208':2022,'650929906032680960':2021,'593899679217930240':2020}
#Weeks in seasons
weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]

#Postgres connection
conn = psycopg2.connect(
    dbname="AutoLMDB",
    user="postgres",
    password="admin",
    host="localhost",
    port="5432"
)

#Create Dataframes
users = pd.DataFrame()
players = pd.DataFrame(sleeper.fill_players())
league = pd.DataFrame()
rosters = pd.DataFrame()
player_performances = pd.DataFrame()
weekly_summaries = pd.DataFrame()
transactions = pd.DataFrame()
playoffs = pd.DataFrame()
drafts = pd.DataFrame()

#Populate each dataframe based on league number and year.
print('Creating dataframes....')
for league_id, league_year in leagues.items():
    users = pd.concat([users, sleeper.get_users(league_id, league_year)], ignore_index=False)
    league_temp, rosters_temp = sleeper.get_rosters(league_id, league_year)
    league = pd.concat([league, league_temp], ignore_index=False)
    rosters = pd.concat([rosters, rosters_temp], ignore_index=False)
    pp_temp, weekly_temp = sleeper.get_matchups(league_id, league_year, weeks)
    player_performances = pd.concat([player_performances, pp_temp], ignore_index=False)
    weekly_summaries = pd.concat([weekly_summaries, weekly_temp], ignore_index=False)
    transactions = pd.concat([transactions, sleeper.get_transactions(league_id, league_year, weeks)], ignore_index=False)
    playoffs = pd.concat([playoffs, sleeper.get_playoffs(league_id, league_year)], ignore_index=False)
    drafts = pd.concat([drafts, sleeper.get_drafts(league_id, league_year)], ignore_index=False)
print('Dataframes created successfully!')


#Load dataframes into Postgres
print('Loading data to tables...')
postgres.create_table_and_insert_data(rosters, "rosters", conn)
postgres.create_table_and_insert_data(users, "users", conn)
postgres.create_table_and_insert_data(league, "league", conn)
postgres.create_table_and_insert_data(player_performances, "player_performances", conn)
postgres.create_table_and_insert_data(weekly_summaries, "weekly_summaries", conn)
postgres.create_table_and_insert_data(transactions, "transactions", conn)
postgres.create_table_and_insert_data(playoffs, "playoffs", conn)
postgres.create_table_and_insert_data(players, "players", conn)
postgres.create_table_and_insert_data(drafts, "drafts", conn)
print('Tables loaded successfully!')

#Success
print('Success!')


#CSV Export paths
#path_league_current = f'C:\\Users\\schmd\\Documents\\AutoLM\\DEV\\league_history_fact.csv'
#path_league_history = f'C:\\Users\\schmd\\Documents\\AutoLM\\DEV\\league_history_detail.csv'
#path_rosters = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\rosters.csv'
#path_performances = f'C:\\Users\\schmd\\Documents\\AutoLM\\DEV\\player_performances_history.csv'
#path_weekly_summaries = f'C:\\Users\\schmd\\Documents\\AutoLM\\DEV\\weekly_summaries_history.csv'
#path_transactions = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\transactions.csv'
#path_playoffs = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\playoffs.csv'
#path_drafts = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\drafts.csv'
#path_players = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\players.csv'
#path_users = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\users.csv'
#path_league = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\league.csv'
#path_performances = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\performances.csv'
#path_weekly_summaries = f'C:\\Users\\schmd\\Documents\\AutoLM\\Base_Tables\\weekly_summaries.csv'


#print('Joining dataframes...')    
#Combine Dataframes for correct curated views
#combined_league_history_detail, combined_roster = sleeper.combine_users(users, league, rosters,players)
#combined_weekly_summaries = sleeper.combine_weekly_matchup_summaries(combined_league_history_detail, weekly_summaries)
#combined_pp = sleeper.combine_player_performances(players, player_performances, combined_league_history_detail)
#combined_transactions = sleeper.combine_transactions(transactions, players, combined_league_history_detail)
#combined_league_history_fact = sleeper.create_league_fact(combined_league_history_detail)


#Load DFs to CSV 

#print('Loading dataframes to CSV....')
#combined_league_history_fact.to_csv(path_league_current, index=False)
#combined_league_history_detail.to_csv(path_league_history, index=False)
#combined_roster.to_csv(path_rosters, index=False)
#combined_pp.to_csv(path_performances, index=False)
#combined_weekly_summaries.to_csv(path_weekly_summaries,index=False)
#combined_transactions.to_csv(path_transactions, index=False)  
#playoffs.to_csv(path_playoffs, index=False)
#drafts.to_csv(path_drafts, index=False)
#players.to_csv(path_players, index=False)
#users.to_csv(path_users, index=False)
#league.to_csv(path_league, index=False)
#rosters.to_csv(path_rosters, index=False)
#player_performances.to_csv(path_performances, index=False)
#weekly_summaries.to_csv(path_weekly_summaries, index=False)
#transactions.to_csv(path_transactions, index=False)