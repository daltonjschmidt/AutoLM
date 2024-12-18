import requests
from pprint import pprint
import json
import pandas as pd
from datetime import date
import sleeper

leagues = {'920151115868565504': 2023,'784647533929566208':2022,'650929906032680960':2021,'593899679217930240':2020}
weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]

#CSV Export paths
path_league_current = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\league_history_fact.csv'
path_league_history = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\league_history_detail.csv'
path_rosters = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\rosters_history.csv'
path_rosters_all = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\rosters_all.csv'
path_performances = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\player_performances_history.csv'
path_weekly_summaries = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\weekly_summaries_history.csv'
path_transactions = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\transactions_history.csv'
path_playoffs = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\playoffs_history.csv'
path_drafts = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\draft_history.csv'
path_players = f'C:\\Users\\schmd\\Documents\\AutoLM\\2023\\players.csv'


users = pd.DataFrame()
players = sleeper.fill_players()
league = pd.DataFrame()
rosters = pd.DataFrame()
player_performances = pd.DataFrame()
weekly_summaries = pd.DataFrame()
transactions = pd.DataFrame()
playoffs = pd.DataFrame()
drafts = pd.DataFrame()


print('Creating dataframes....')
for league_id, league_year in leagues.items():
    #Create all base Dataframes
    users = pd.concat([users, sleeper.get_users(league_id, league_year)], ignore_index=False)
    league_temp, rosters_temp = sleeper.get_rosters(league_id, league_year)
    league = pd.concat([league, league_temp], ignore_index=False)
    rosters = pd.concat([rosters, rosters_temp], ignore_index=False)
    pp_temp, weekly_temp = sleeper.get_matchups(league_id, league_year, weeks)
    player_performances = pd.concat([player_performances, pp_temp], ignore_index=False)
    weekly_summaries = pd.concat([weekly_summaries, weekly_temp], ignore_index=False)
    transactions = pd.concat([transactions, sleeper.get_transactions(league_id, league_year, weeks)], ignore_index=False)
    playoffs = pd.concat([playoffs, sleeper.get_playoffs(league_id, league_year)], ignore_index=False)
    drafts = pd.concat([drafts, sleeper.get_drafts(league_id)], ignore_index=False)




print('Joining dataframes...')    
#Combine Dataframes for correct curated views
combined_league_history_detail, combined_roster = sleeper.combine_users(users, league, rosters,players)
combined_weekly_summaries = sleeper.combine_weekly_matchup_summaries(combined_league_history_detail, weekly_summaries)
combined_pp = sleeper.combine_player_performances(players, player_performances, combined_league_history_detail)
combined_transactions = sleeper.combine_transactions(transactions, players, combined_league_history_detail)
combined_league_history_fact = sleeper.create_league_fact(combined_league_history_detail)

#combined_league_current_year = combined_league[combined_league['year'] == 2023]


print('Loading dataframes to CSV....')
combined_league_history_fact.to_csv(path_league_current, index=False)
combined_league_history_detail.to_csv(path_league_history, index=False)
combined_roster.to_csv(path_rosters, index=False)
combined_pp.to_csv(path_performances, index=False)
combined_weekly_summaries.to_csv(path_weekly_summaries,index=False)
combined_transactions.to_csv(path_transactions, index=False)  
playoffs.to_csv(path_playoffs, index=False)
drafts.to_csv(path_drafts, index=False)
players.to_csv(path_players, index=False)
rosters.to_csv(path_rosters_all, index=False)

print('Success!')
