import requests
from pprint import pprint
import json
import pandas as pd
from datetime import date


def fill_players():
    #Get json response from sleeper to dictionary
    player_response = requests.get(f'https://api.sleeper.app/v1/players/nfl')
    #Convert response dictionry to DF on index player_id
    players_df = pd.DataFrame.from_dict(player_response.json(), orient='index')
    non_float_rows =players_df[players_df['player_id'].apply(lambda x: pd.to_numeric(x, errors='coerce') is None)]
    #return dataframe
    return non_float_rows

df = fill_players()
print(df["player_id"])