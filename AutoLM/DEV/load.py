from pprint import pprint
import pandas as pd
from sqlalchemy import create_engine
from dash import html

def get_data(query):
    print('Loading query')
    #Postgres connection
    engine = create_engine('postgresql://schmd:password@localhost:5432/AutoLMDB')

    #Load query into df via engine
    df = pd.read_sql_query(query, engine)

    # Close the connection
    engine.dispose()

    print('Query loaded!')
    #Print Results
    return df

def interpolate_color(start_rgb, end_rgb, val):
    """
    Interpolate between two RGB colors.
    :param start_rgb: Tuple representing the RGB value of the starting color.
    :param end_rgb: Tuple representing the RGB value of the ending color.
    :param val: Value between 0 and 1 representing the position between start and end.
    :return: Tuple representing the interpolated RGB color.
    """
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * val)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * val)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * val)
    return f'rgb({r}, {g}, {b})'

def discrete_background_color_bins(df, column='Total Wins'):
    min_wins = df[column].min()
    max_wins = df[column].max()

    styles = []
    legend = []

    # Define RGB values for green, yellow, and red
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    red = (255, 0, 0)

    for wins in range(min_wins, max_wins + 1):
        # Normalize wins to a value between 0 and 1
        val = (wins - min_wins) / (max_wins - min_wins)

        # Interpolate between green and yellow, and between yellow and red
        if val <= 0.5:
            backgroundColor = interpolate_color(green, yellow, val * 2)
        else:
            backgroundColor = interpolate_color(yellow, red, (val - 0.5) * 2)

        styles.append({
            'if': {
                'filter_query': f'{{{column}}} = {wins}',
                'column_id': column
            },
            'backgroundColor': backgroundColor,
            'color': 'white' if val > 0.5 else 'black'  # Set text color based on background color brightness
        })

        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(str(wins), style={'paddingLeft': '2px'})
            ])
        )

    return styles, html.Div(legend, style={'padding': '5px 0 5px 0'})
