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
        "year": int(year),
        "user_year": str(year)  + ':' + str(item["user_id"])[:5]
    } for item in user_response]

    users_df = pd.DataFrame(user_data)

    return users_df

def fill_players():
    #Get json response from sleeper to dictionary
    player_response = requests.get(f'https://api.sleeper.app/v1/players/nfl')
    #Convert response dictionry to DF on index player_id
    players_df = pd.DataFrame.from_dict(player_response.json(), orient='index')
    players_df = players_df[pd.to_numeric(players_df['player_id'], errors='coerce').notnull()]
    #return dataframe
    return players_df

def get_rosters(league_number, year):
    # Fetch the roster response from the API
    roster_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/rosters').json()
    
    # Process each roster item
    league_data = []
    roster_data = []

    for item in roster_response:
        # Safely get 'metadata' and handle cases where it might be None
        metadata = item.get("metadata", {})
        settings = item.get("settings", {})
        
        # Ensure that metadata is a dictionary, if it's None or other type, default to empty dictionary
        if metadata is None:
            metadata = {}
        
        # Build the league_data list
        league_data.append({
            "roster_id": item.get("roster_id", None),  # Default to None if not present
            "owner_id": item.get("owner_id", None),    # Default to None if not present
            "streak": metadata.get("streak", 0),       # Use .get() with default value
            "record": metadata.get("record", "N/A"),   # Default to "N/A" if not present
            "wins": int(settings.get("wins", 0)),      # Default to 0 if not present
            "losses": int(settings.get("losses", 0)),  # Default to 0 if not present
            "ties": int(settings.get("ties", 0)),      # Default to 0 if not present
            "possible_points_for": float(settings.get("ppts", 0.0)),  # Default to 0.0 if not present
            "actual_points_for": float(settings.get("fpts", 0.0)),    # Default to 0.0 if not present
            "points_against": float(settings.get("fpts_against", 0.0)),  # Default to 0.0 if not present
            "division": settings.get("division",1),  # Default to "Unknown" if not present
            "moves": settings.get("total_moves", 0),  # Default to 0 if not present
            "year": int(year),  # Convert year to int
            "user_year": f'{year}:{str(item.get("owner_id", "")[:5])}',  # Handle missing owner_id
            "roster_year": f'{str(league_number)[:5]}:{str(item.get("roster_id", ""))}'  # Handle missing roster_id
        })

        # Build the roster_data list
        for player in item.get("players", []):
            roster_data.append({
                "year": int(year),
                "roster_id": item.get("roster_id"),
                "player_id": player,
                "roster_year": f'{str(league_number)[:5]}:{str(item.get("roster_id", ""))}',
                "year_roster_player": f'{year}:{str(item.get("roster_id", ""))}:{player}',
            })

    league_df = pd.DataFrame(league_data)
    roster_df = pd.DataFrame(roster_data)

    return league_df, roster_df


def get_matchups(league_number, year, weeks):
    player_performance = []
    weekly_matchups = []
    
    # Dictionary to track matchups by matchup_id and week
    matchup_dict = {}

    for week in weeks:
        # Fetch matchup data for the week
        matchup_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/matchups/{week}').json()

        for matchup in matchup_response:
            matchup_id = matchup.get('matchup_id')
            roster_id = matchup.get('roster_id')
            points = matchup.get('points', 0)
            players = matchup.get('players', {})
            player_points = matchup.get('players_points', {})
            starters = matchup.get('starters', [])

            # Process player performance data
            for player_id, ppoints in player_points.items():
                row = {
                    "week_number": int(week),
                    "roster_id": roster_id,
                    "matchup_id": matchup_id,
                    "player_id": player_id,
                    "player_points": float(ppoints),
                    "starter": player_id in starters,
                    "year": int(year),
                    "roster_year": f'{str(league_number)[:5]}:{str(roster_id)}',
                    "year_week_matchup": f'{year}:{week}:{matchup_id}',
                    "year_roster_player": f'{year}:{roster_id}:{player_id}'
                }
                player_performance.append(row)

            # Check if the matchup already exists
            key = (matchup_id, week)
            if key in matchup_dict:
                existing = matchup_dict[key]
                existing["roster_id_2"] = roster_id
                existing["roster_year_2"] = f'{str(league_number)[:5]}:{str(roster_id)}'
                existing["total_points_2"] = float(points)
            else:
                # New matchup entry
                matchup_entry = {
                    "week_number": int(week),
                    "year": int(year),
                    "matchup_id": matchup_id,
                    "roster_id_1": roster_id,
                    "roster_year_1": f'{str(league_number)[:5]}:{str(roster_id)}',
                    "total_points_1": float(points),
                    "roster_id_2": None,
                    "total_points_2": None,
                    "year_week_matchup": f'{year}:{week}:{matchup_id}'
                }
                matchup_dict[key] = matchup_entry
                weekly_matchups.append(matchup_entry)

    # Convert lists to DataFrames
    performance_df = pd.DataFrame(player_performance)
    weekly_df = pd.DataFrame(weekly_matchups)
    performance_df.dropna(subset=['matchup_id'],inplace=True)
    weekly_df.dropna(subset=['matchup_id'], inplace=True)

    return performance_df, weekly_df

def get_transactions(league_number, year, weeks):
    transaction_dict = []

    for week in weeks:
        # Fetch the transaction response from the API
        transact_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/transactions/{week}').json()
        
        if transact_response:
            for transact in transact_response:
                transaction_id = transact.get("transaction_id", None)
                type = transact.get("type", None)
                settings = transact.get("settings", {})
                metadata = transact.get("metadata", {})
                creator = transact.get("creator", None)
                adds = transact.get("adds", {})
                drops = transact.get("drops", {})
                roster_ids = transact.get("roster_ids", [])
                consenter_ids = transact.get("consenter_ids", [])
                draft_picks = transact.get("draft_picks", [])
                
                # Ensure settings and metadata are dictionaries
                if settings is None:
                    settings = {}
                if metadata is None:
                    metadata = {}
                
                # Extract values from settings
                waiver_bid = settings.get("waiver_bid", None)
                seq = settings.get("seq", None)
                is_counter = settings.get("is_counter", None)
                
                # Extract notes from metadata
                notes = metadata.get("notes", None)

                # Ensure adds and drops are dictionaries
                if adds is None:
                    adds = {}
                if drops is None:
                    drops = {}
                
                # Process adds
                for player_id, roster_id in adds.items():
                    transaction_dict.append({
                        "week": int(week),
                        "year": int(year),
                        "transaction_id": transaction_id,
                        "creator_id": creator,
                        "player_id": player_id,
                        "roster_id": roster_id,
                        "roster_year": f'{str(league_number)[:5]}:{str(roster_id)}',
                        "add_drop": "Add",
                        "type": type,
                        "waiver_bid": waiver_bid,
                        "seq": seq,
                        "is_counter": is_counter,
                        "notes": notes
                    })

                # Process drops
                for player_id, roster_id in drops.items():
                    transaction_dict.append({
                        "week": int(week),
                        "year": int(year),
                        "transaction_id": transaction_id,
                        "creator_id": creator,
                        "player_id": player_id,
                        "roster_id": roster_id,
                        "roster_year": f'{str(league_number)[:5]}:{str(roster_id)}',
                        "add_drop": "Drop",
                        "type": type,
                        "waiver_bid": waiver_bid,
                        "seq": seq,
                        "is_counter": is_counter,
                        "notes": notes
                    })

                # Process draft picks
                for trade in draft_picks:
                    transaction_dict.append({
                        "week": int(week),
                        "year": int(year),
                        "transaction_id": transaction_id,
                        "creator_id": creator,
                        "roster_id": trade.get("roster_id", None),
                        "roster_year": f'{str(league_number)[:5]}:{str(trade.get("roster_id", ""))}',
                        "add_drop": "Pick Trade",
                        "type": type,
                        "pick_season": int(trade.get("season", 0)),
                        "pick_round": int(trade.get("round", 0)),
                        "original_pick_owner": trade.get("roster_id", None),
                        "previous_pick_owner": trade.get("previous_owner_id", None),
                        "new_pick_owner_id": trade.get("owner_id", None),
                        "seq": seq,
                        "is_counter": is_counter,
                        "notes": notes
                    })

    # Convert list of transactions to DataFrame
    transact_df = pd.DataFrame(transaction_dict)
    return transact_df
def get_playoffs(league_number, year):
    # Fetch playoff bracket data
    url = f'https://api.sleeper.app/v1/league/{league_number}/winners_bracket'
    playoff_bracket = pd.DataFrame(requests.get(url).json())

    # Initialize DataFrame for final standings
    final_standings = pd.DataFrame(columns=['roster_id', 'rank', 'roster_year'])

    # Filter final round where 'p' (position) is not null and sort by 'p'
    final_round = playoff_bracket[playoff_bracket['p'].notnull()].sort_values(by='p')

    # Calculate rank and build final standings DataFrame
    rank = 1
    for _, row in final_round.iterrows():
        # Create a DataFrame for the current matchups and concatenate
        matchups_df = pd.DataFrame({
            "roster_id": [row['w'], row['l']],
            "rank": [rank, rank + 1],
            "roster_year": [f"{str(league_number)[:5]}:{row['w']}", f"{str(league_number)[:5]}:{row['l']}"]
        })
        final_standings = pd.concat([final_standings, matchups_df], ignore_index=True)
        rank += 2

    # Initialize list for playoff records
    playoff_records = []

    # Get unique roster IDs
    unique_roster_ids = set(playoff_bracket['w']).union(set(playoff_bracket['l']))

    # Calculate wins and losses for each roster_id
    for roster_id in unique_roster_ids:
        wins = playoff_bracket[playoff_bracket['w'] == roster_id].shape[0]
        losses = playoff_bracket[playoff_bracket['l'] == roster_id].shape[0]
        playoff_records.append({
            "roster_id": roster_id,
            "wins": wins,
            "losses": losses,
            "year": int(year),
            "roster_year": f"{str(league_number)[:5]}:{roster_id}"
        })

    # Create DataFrame from playoff records
    playoff_record_df = pd.DataFrame(playoff_records)

    # Merge final standings with playoff records and calculate additional columns
    final_playoffs = final_standings.merge(playoff_record_df, on='roster_year', how='outer', suffixes=['', '_record'])
    final_playoffs = final_playoffs.sort_values(by='rank').reset_index(drop=True)

    # Add additional columns for champion status and win percentage
    final_playoffs["is_champion"] = final_playoffs["rank"] == 1
    final_playoffs["win_perc"] = final_playoffs.apply(
        lambda row: row['wins'] / (row['wins'] + row['losses']) if (row['wins'] + row['losses']) > 0 else 0,
        axis=1
    )

    if 'roster_id_record' in final_playoffs.columns:
        final_playoffs.drop(columns='roster_id_record', inplace=True)
    return final_playoffs

def get_drafts(league_number, year):
    try:
        # Fetch draft info
        draft_info_response = requests.get(f'https://api.sleeper.app/v1/league/{league_number}/drafts')
        draft_info_response.raise_for_status()  # Raise an error for bad HTTP status codes
        draft_info = draft_info_response.json()
        
        if not draft_info:
            raise ValueError("No draft information found.")

        draft_info = draft_info[0]
        draft_id = str(draft_info['draft_id'])

        # Fetch draft picks
        draft_results_response = requests.get(f'https://api.sleeper.app/v1/draft/{draft_id}/picks')
        draft_results_response.raise_for_status()  # Raise an error for bad HTTP status codes
        draft_results = draft_results_response.json()

        # Create DataFrame
        draft_results_df = pd.DataFrame(draft_results)

        # Add 'roster_year' and 'year' columns
        draft_results_df['roster_year'] = str(league_number)[:5] + ':' + draft_results_df["roster_id"].astype(str)
        draft_results_df["year"] = int(year)

        # Drop 'metadata' column if it exists
        if 'metadata' in draft_results_df.columns:
            draft_results_df = draft_results_df.drop("metadata", axis=1)

        draft_results_df.drop(columns="reactions", inplace=True)

        return draft_results_df

    except requests.RequestException as e:
        # Handle HTTP errors
        print(f"HTTP Request failed: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

    except ValueError as e:
        # Handle errors related to the absence of draft information
        print(f"ValueError: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure






