import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

from src.db import reference_sets as db


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = db.ref_set_stats_to_dataframe(1)

fig = px.bar(df, x=df.index, y="pitch_count_distance", barmode="group")

app.layout = html.Div(children=[
    html.H1(children="Reference Data for Similarity"),
    html.Div(children='''Data: ~ 17000 call-and-response pairs extracted from melodies crawled from Theorytab'''),
    dcc.Graph(
        id='test-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)