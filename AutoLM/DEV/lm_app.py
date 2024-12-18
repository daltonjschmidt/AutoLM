from dash import Dash, html, dcc, callback, Output, Input, dash, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import load


league_query = """SELECT 
    roster_id as "Roster ID",
    owner_id as "Manager ID",
    streak as "Streak",
    record as "Record",
    wins as "Regular Season Wins",
    losses as "Losses",
    ties as "Ties",
    possible_points_for as "Possible Points For",
    actual_points_for as "Actual Points For",
    points_against as "Points Against",
    division as "Division",
    moves as "Moves",
    year as "Year",
    user_year,
    roster_year,
    win_perc as "Win Percentage",
    championships as Championships,
    display_name as "Display Name",
    total_wins AS "Total Wins"
FROM 
    public.vw_league;"""

rw_query = """SELECT 
    year as "Year", 
    week_number as "Week Number", 
    display_name as "Manager", 
    running_total_win_flag as "Running Wins"
FROM 
    public.vw_running_wins;"""


#Load Query into DF
lq = pd.DataFrame(load.get_data(league_query))
rw = pd.DataFrame(load.get_data(rw_query))
                  
#Select only columns for Table
league_cols = ['Year', 'Display Name', 'Total Wins', 'Regular Season Wins', 'Losses', 'Ties', 'Actual Points For', 'Points Against', 'Possible Points For', 'Win Percentage' ]
league_table = lq[league_cols].sort_values('Total Wins', ascending=False)

#Initialize Dash
app = dash.Dash(__name__)

#Create Style for Table
(styles, legend) = load.discrete_background_color_bins(league_table, 'Total Wins')

#Initialize HTML Div
app.layout = html.Div(
    [
        html.H4("League of Professional Jerkoffs"),
        html.P("Select Year:"),
        dcc.Dropdown(
            id="year-dropdown",
            options=[{'label': year, 'value': year} for year in league_table['Year'].unique()],
            value=league_table['Year'].max(),
            clearable=False,
            multi=False
        ),
        dcc.Graph(id="graph"),
        dcc.Graph(id='line'),
        dash_table.DataTable(
            id='table',
            columns=[
                {"name": i, "id": i, "type": "numeric", "format": {"specifier": ".2%"}}
                if i == 'Win Percentage' else {"name": i, "id": i} for i in league_table.columns
            ],
            data=league_table.to_dict('records'),
            style_table={'overflowX': 'auto'},  # Horizontal scroll
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_cell={'textAlign': 'center'},
            # Add more style options as needed
            style_data_conditional=styles
        )
    ]
)


#Callback for bar chart
@app.callback(
    Output("graph", "figure"),
    Input("year-dropdown", "value")
)

#Update function for bar chart
def update_bar_chart(selected_year):
    filtered_df = lq[lq['Year'] == selected_year]
    filtered_df = filtered_df.sort_values(by='Total Wins', ascending=True)
    fig = px.bar(filtered_df, x="Display Name", y="Total Wins", 
                barmode="group")
    # Update layout to remove axis labels
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)

    return fig

@app.callback(
    Output("line", "figure"),
    Input("year-dropdown", "value")
)

def update_line_chart(selected_year):
    filtered_df = rw[rw['Year'] == selected_year]
    fig = px.line(filtered_df, x="Week Number", y="Running Wins", color="Manager",
                  title="Running Wins Over Weeks")
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)

    return fig

#Callback for table
@app.callback(
    Output('table', 'data'),
    Input('year-dropdown', 'value')
)

#Update function for table
def update_table_data(selected_years):
    filtered_df = league_table[league_table['Year'] == selected_years]
    return filtered_df.to_dict('records')



#Run Dash APP
if __name__ == '__main__':
    app.run_server(debug=True)