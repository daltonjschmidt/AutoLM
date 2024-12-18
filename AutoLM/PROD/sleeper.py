import requests
from pprint import pprint
import json
import pandas as pd
from datetime import date

#Users API Call
def get_users(league_number, year):
    user_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/users').json()
    
    user_data = [{
        "user_id": item["user_id"],
        "display_name": item["display_name"],
        "avatar": item.get("avatar", ""),
        "team_name": item.get("metadata", {}).get("team_name", item["display_name"]),
        "is_owner": item.get("is_owner", False),
        "year": year,
        "user_year": str(year)  + ':' + str(item["user_id"])[:5]
    } for item in user_response]

    users_df = pd.DataFrame(user_data)

    return users_df

def fill_players():
    #Get json response from sleeper to dictionary
    player_response = requests.get(f'https://api.sleeper.app/v1/players/nfl')
    #Convert response dictionry to DF on index player_id
    players_df = pd.DataFrame.from_dict(player_response.json(), orient='index')
    #return dataframe
    return players_df

def get_rosters(league_number, year):
    roster_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/rosters').json()

    league_data = [{
        "roster_id": item["roster_id"],
        "owner_id": item["owner_id"],
        "streak": item["metadata"].get("streak", 0),
        "record": item["metadata"]["record"],
        "wins": item["settings"].get("wins", 0),
        "losses": item["settings"].get("losses", 0),
        "ties": item["settings"].get("ties", 0),
        "possible_points_for": item["settings"].get("ppts", 0),
        "actual_points_for": item["settings"].get("fpts", 0),
        "points_against": item["settings"].get("fpts_against", 0),
        "division": item["settings"].get("division"),
        "moves": item["settings"].get("total_moves", 0),
        "year": year,
        "user_year": str(year)  + ':' + str(item["owner_id"])[:5],
        "roster_year":  str(league_number)[:5] + ':'+ str(item["roster_id"])
    } for item in roster_response]

    roster_data = [{
        "year": year,
        "roster_id": item["roster_id"],
        "player_id": player,
        "roster_year": str(league_number)[:5] + ':'+ str(item["roster_id"]),
        "year_roster_player": str(year) + ':'+ str(item["roster_id"]) + ':' + str(player),
    } for item in roster_response for player in item["players"]]

    league_df = pd.DataFrame(league_data)
    roster_df = pd.DataFrame(roster_data)

    return league_df, roster_df

def get_matchups(league_number, year, weeks):
    player_performance = []
    weekly_matchups = []
    for week in weeks:
        matchup_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/matchups/{week}').json()

        for matchup in matchup_response:
            matchup_id = matchup['matchup_id']
            roster_id = matchup['roster_id']
            points = matchup['points']
            players = matchup['players']
            player_points = matchup['players_points']
            starters = matchup['starters']

            for player_id, ppoints in player_points.items():  
                row = {
                    "week_number": week,
                    "roster_id": roster_id,
                    "matchup_id": matchup_id,
                    "player_id": player_id,
                    "player_points": ppoints,
                    "starter": player_id in starters,
                    "year": year,
                    "roster_year": str(league_number)[:5] + ':'+ str(roster_id),
                    "year_week_matchup": str(year) + ':' + str(week) + ':' + str(matchup_id),
                    "year_roster_player": str(year) + ':' + str(roster_id) + ':' + str(player_id)
                }
                player_performance.append(row)

            found_matchup = False
            for existing_matchup in weekly_matchups:
                if existing_matchup["matchup_id"] == matchup_id and existing_matchup["week_number"] == week:
                    existing_matchup["roster_id_2"] = roster_id
                    existing_matchup["roster_year_2"] = str(league_number)[:5] + ':'+ str(roster_id)
                    existing_matchup["total_points_2"] = points
                    found_matchup = True
                    break

            if not found_matchup:
                weekly_matchups.append({
                    "week_number": week,
                    "year": year,
                    "matchup_id": matchup_id,
                    "roster_id_1": roster_id,
                    "roster_year_1": str(league_number)[:5] + ':'+ str(roster_id),
                    "total_points_1": points,
                    "roster_id_2": None,
                    "total_points_2": None,
                    "year_week_matchup": str(year) + ':' + str(week) + ':' + str(matchup_id)
                })
    performance_df = pd.DataFrame(player_performance)
    weekly_df = pd.DataFrame(weekly_matchups)
    return performance_df, weekly_df

def get_transactions(league_number, year, weeks):
    transaction_dict = []
    for week in weeks:
        transact_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/transactions/{week}').json()
        if transact_response is not None:
            for transact in transact_response:
                transaction_id = transact["transaction_id"]
                type = transact["type"]
                settings = transact["settings"]
                metadata = transact["metadata"]
                creator = transact["creator"]
                adds = transact["adds"]
                drops = transact["drops"]
                roster_ids = transact["roster_ids"]
                consenter_ids = transact["consenter_ids"]
                draft_picks = transact["draft_picks"]
                waiver_bid = None
                seq = None
                is_counter = None
                notes = None
                if settings is not None:
                    if "waiver_bid" in settings:
                        waiver_bid = settings["waiver_bid"]
                    if "seq" in settings:
                        seq = settings["seq"]
                    if "is_counter" in settings:
                        is_counter = settings["is_counter"]
                if metadata is not None:
                    notes = metadata["notes"]

                if adds is not None:
                    for player_id, roster_id in adds.items():
                        transaction_dict.append({
                            "week": week,
                            "year": year,
                            "transaction_id": transaction_id,
                            "creator_id": creator,
                            "player_id": player_id ,
                            "roster_id": roster_id,
                            "roster_year": str(league_number)[:5] + ':'+ str(roster_id),
                            "add_drop": "Add",
                            "type": type,
                            "waiver_bid": waiver_bid,
                            "seq": seq,
                            "is_counter": is_counter,
                            "notes": notes
                        })

                if drops is not None:    
                    for player_id, roster_id in drops.items():
                        transaction_dict.append({
                            "week": week,
                            "year": year,
                            "transaction_id": transaction_id,
                            "creator_id": creator,
                            "player_id": player_id ,
                            "roster_id": roster_id,
                            "roster_year": str(league_number)[:5] + ':'+ str(roster_id),
                            "add_drop": "Drop",
                            "type": type,
                            "waiver_bid": waiver_bid,
                            "seq": seq,
                            "is_counter": is_counter,
                            "notes": notes
                        })

                if draft_picks is not None:
                    for trade in draft_picks:
                        transaction_dict.append({
                            "week": week,
                            "year": year,
                            "transaction_id": transaction_id,
                            "creator_id": creator,
                            "roster_id": roster_id,
                            "roster_year": str(league_number)[:5] + ':'+ str(roster_id),
                            "add_drop": "Pick Trade",
                            "type": type,
                            "pick_season": trade["season"],
                            "pick_round": trade["round"],
                            "original_pick_owner": trade["roster_id"],
                            "previous_pick_owner": trade["previous_owner_id"],
                            "new_pick_owner_id": trade["owner_id"],
                            "seq": seq,
                            "is_counter": is_counter,
                            "notes": notes
                    })
    transact_df = pd.DataFrame(transaction_dict)
    return transact_df

def get_playoffs(league_number, year): 
    # Retrieving playoff bracket data
    playoff_bracket = pd.DataFrame(requests.get(f'https://api.sleeper.app/v1/league/{league_number}/winners_bracket').json())
    
    # Initialize DataFrame to store final standings
    final_standings = pd.DataFrame(columns=['roster_id', 'rank'])
    
    # Filter final round
    final_round = playoff_bracket[playoff_bracket['p'].notnull()].sort_values(by='p')
    
    # Calculate rank based on finishing position and assign to DataFrame
    rank = 1
    for index, row in final_round.iterrows():
        final_standings = pd.concat([
            final_standings,
            pd.DataFrame({"roster_id": [row['w'], row['l']], "rank": [rank, rank+1], "roster_year": [f"{league_number[:5]}:{row['w']}", f"{league_number[:5]}:{row['l']}"]})
        ], ignore_index=True)
        rank += 2
    
    # Initialize list to store playoff records
    playoff_records = []
    
    # Get unique roster IDs
    unique_roster_ids = set(playoff_bracket['w']).union(set(playoff_bracket['l']))
    
    # Calculate wins and losses and append to list
    for roster_id in unique_roster_ids:
        wins = playoff_bracket[playoff_bracket['w'] == roster_id]['w'].count()
        loses = playoff_bracket[playoff_bracket['l'] == roster_id]['l'].count()
        playoff_records.append({
            "wins": wins,
            "losses": loses,
            "year": year,
            "roster_year": f"{league_number[:5]}:{roster_id}"
        })

    # Create DataFrame from list of dictionaries
    playoff_record = pd.DataFrame(playoff_records)
    
    final_playoffs = final_standings.merge(playoff_record, on='roster_year', how='outer',suffixes=['','_2']).sort_values(by='rank').reset_index(drop=True)
    final_playoffs["is_champion"] = final_playoffs["rank"] == 1
    final_playoffs["win_perc"] = final_playoffs.apply(lambda row: row['wins'] / (row['wins'] + row['losses']) , axis=1)

    return final_playoffs

def get_drafts(league_number, year):
    draft_info  = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/drafts').json()
    draft_info = draft_info[0]
    draft_id = str(draft_info['draft_id'])
    draft_results_df = pd.DataFrame(requests.get(f'https://api.sleeper.app/v1/draft/{draft_id}/picks').json())
    draft_results_df['roster_year'] =  str(league_number)[:5] + ':'+ draft_results_df["roster_id"].astype(str)
    draft_results_df["year"] = year
    return draft_results_df

#def combine_users(users_df, league_df, rosters_df,players_df):
    #Create column list for final dataframes
    league_cols = ['user_id', 'roster_id', 'team_name', 'display_name', 'year', 'user_year', 'roster_year']
    player_cols = ['player_id', 'year', 'user_year', 'roster_year', 'user_id','year_roster_player']

    #left join league data onto users data User_ID:Owner_ID
    league_data = users_df.merge(league_df, left_on='user_year', right_on='user_year', how='left', suffixes=(['','_l']))
    filtered_league_df = pd.DataFrame(league_data, columns=league_cols)

    #Left join the new filtered leaague df with rosters_df on roster_id
    roster_data = filtered_league_df.merge(rosters_df, on='roster_year', suffixes =(['','_p']), how='left')
    roster_data = pd.DataFrame(roster_data, columns=player_cols)
    roster_data["current_owner"] = roster_data.apply(lambda row: True if row['year'] == max(leagues.values()) else False, axis=1)
    
    #Make changes to league data
    league_data = league_data.drop(columns=['year_l'])
    league_data["win_perc"] = league_data.apply(lambda row: row['wins'] / (row['wins'] + row['losses'] + row['ties']) , axis=1)

    #Return the filtered dfs
    return league_data, roster_data

#def combine_weekly_matchup_summaries(combined_league_df,  weekly_summary_df):

    # Define columns of interest
    summary_cols = ['year_week_matchup','week_number', 'year', 'matchup_id', 'roster_id_1','roster_year_1', 'display_name', 'total_points_1', 'display_name_y','roster_id_2', 'roster_year_2', 'total_points_2']
    combined_league_df = pd.DataFrame(combined_league_df, columns=['roster_year', 'display_name'])
    # Merge weekly summary with league data for both rosters
    combined_summary = weekly_summary_df.merge(combined_league_df, left_on='roster_year_1', right_on='roster_year', how='left', suffixes=('','_x')) \
                                         .merge(combined_league_df, left_on='roster_year_2', right_on='roster_year', how='left', suffixes=('', '_y'))\
    
    combined_summary.drop(columns=['roster_year', 'roster_year_y'], inplace=True)

    def find_winner(row):
        result = None
        if not pd.isnull(row['matchup_id']):
            if row['total_points_1'] > row['total_points_2']:
                result = row['roster_year_1']
            else:
                result = row['roster_year_2']
        return result
    
    def find_loser(row):
        result = None
        if not pd.isnull(row['matchup_id']):
            if row['total_points_1'] < row['total_points_2']:
                result = row['roster_year_1']
            else:
                result = row['roster_year_2']
        return result
    
    def find_ties(row):
        result = None
        if not pd.isnull(row['matchup_id']):
            if row['total_points_1'] == row['total_points_2']:
                result = 1
            else:
                result = 0
        return result

    # Select only necessary columns
    combined_summary = combined_summary[summary_cols]
    combined_summary['winner'] = combined_summary.apply(find_winner, axis=1)
    combined_summary['loser'] = combined_summary.apply(find_loser, axis=1)
    combined_summary['tie'] = combined_summary.apply(find_ties, axis=1)


    return combined_summary

#def combine_player_performances(players_df, player_performance_df, combined_league_df):

    #left outer join team name to player performance
    perf_cols = ['year_week_matchup', 'year_roster_player', 'year', 'week_number', 'roster_id','roster_year', 'matchup_id', 'player_id', 'player_points', 'starter','display_name', 'team_name']
    player_cols = perf_cols + ['full_name', 'first_name', 'last_name', 'team', 'position', 'age']
    player_to_user = player_performance_df.merge(combined_league_df, on='roster_year', suffixes=('', '_2'))
    player_to_user = player_to_user[perf_cols]

    #left outer join player info to player performance
    player_to_user = player_to_user.merge(players_df, on='player_id', suffixes=('', '_2'))
    player_to_user = player_to_user[player_cols]

    return player_to_user

#def combine_transactions(transactions_df, players_df, league_df):
    #left outer join team name to player performance
    league_cols = list(transactions_df.columns) + ['owner_id', 'team_name', 'display_name']
    player_cols = league_cols + ['full_name', 'first_name', 'last_name', 'team', 'position', 'age']

    combined_transactions = transactions_df.merge(league_df, on='roster_year', suffixes=('', '_2'), how='left')
    combined_transactions = combined_transactions[league_cols]

    combined_transactions = combined_transactions.merge(players_df, on='player_id', suffixes=('', '_2'), how='left')
    combined_transactions = combined_transactions[player_cols]

    return combined_transactions

#def create_league_fact(combined_league_df):
    combined_league_history_fact = pd.DataFrame(combined_league_df, columns=['user_id', 'display_name', 'year'])
    
    # Convert 'user_id' to string
    combined_league_history_fact['user_id'] = combined_league_history_fact['user_id'].astype(str)

    # Aggregate how many years each user has been in the league
    years_in_league = combined_league_history_fact.groupby('user_id').size().reset_index(name='years_in_league')

    # Check if each user is active in the current year
    current_year = 2023
    combined_league_history_fact['active'] = combined_league_history_fact['user_id'].isin(
        combined_league_history_fact.loc[combined_league_history_fact['year'] == current_year, 'user_id']
    )

    # Drop duplicates on 'user_id'
    combined_league_history_fact = combined_league_history_fact.drop_duplicates(subset='user_id')

    # Merge 'years_in_league' back to the main DataFrame
    combined_league_history_fact = pd.merge(combined_league_history_fact, years_in_league, on='user_id', how='left')

    # Fill NaN values in 'years_in_league' with 0 (for users who have no history)
    combined_league_history_fact['years_in_league'] = combined_league_history_fact['years_in_league'].fillna(0).astype(int)

    #Find championships
    

    return combined_league_history_fact




