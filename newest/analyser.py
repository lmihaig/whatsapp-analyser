import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date
from wordcloud import WordCloud


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO], meta_tags=[
                {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=4)
    ], className="mt-2 mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3)
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=3)
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([

                ])
            ])
        ], width=6),
    ], className="mb-2")
])

if __name__ == "__main__":
    app.run_server(debug=True)
