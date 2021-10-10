import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import re
from datetime import date
from wordcloud import WordCloud


def read_chat(file):
    """reads Whatsapp chat file into a list of strings"""
    chat_file = open(file, "r", encoding="utf-8")
    text = chat_file.read()
    content = text.splitlines()  # list of strings
    return content


def clearchat(chat):
    """combines multi-line messages without a proper date-time in a single message"""
    date_time_pattern = re.compile("^[0-3][0-9]\/[0-1][0-9]\/\d{4},")
    for i in range(len(chat)):
        if date_time_pattern.search(chat[i]) is None:
            chat[i-1] = chat[i-1] + " " + chat[i]
            chat[i] = "NotAValidEntry"

    for i in range(len(chat)):
        if chat[i].split(" ")[0] == "NotAValidEntry":
            chat[i] = "NotAValidEntry"

    while True:
        try:
            chat.remove("NotAValidEntry")
        except ValueError:
            break
    return chat


def build_df(chat):
    date_list = []
    time = []
    name = []
    content = []

    for text in chat:
        date_list.append(text.split(",")[0])
        time.append(text.split(",")[1].split("-")[0])
        name.append(text.split("-")[1].split(":")[0])
        try:
            content.append(text.split(":")[2])
        except IndexError:
            content.append("Missing Text")

    df = pd.DataFrame(list(zip(date_list, time, name, content)),
                      columns=["Date", "Time", "Name", "Content"])
    return df


chat = read_chat("chat.txt")
chat = clearchat(chat)
df = build_df(chat)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])

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
                    dbc.CardLink("lmihaig", target="_blank",
                                 href="https://github.com/lmihaig/whatsapp-analyser")
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
