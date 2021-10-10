import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import re
from datetime import date
from wordcloud import WordCloud
from base64 import b64decode


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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.CardLink("WhatsApp Chat Analyser by lmihaig", target="_blank",
                                 href="https://github.com/lmihaig/whatsapp-analyser")
                ],  className='align-self-center')
            ])
        ], width=5),
        dbc.Col([
            dcc.Upload([
                'Drag and Drop or ',
                html.A('Select a File')], id="upload-chat",
                style={
                'width': '80%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
            })])
    ], className="mt-2 mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TOTAL MESSAGES", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="total-messages")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3)
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TEST", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2("test")
                ], style={"textAlign": "center"})
            ])
        ], width=3)
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="line-chart", figure={})
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="bar-chart", figure={})
                ])
            ])
        ], width=6),
    ], className="mb-2"),
    dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="pie-chart", figure={})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="word-cloud", figure={})
                    ])
                ])
            ], width=6),
            ], className="mb-2")
])


@app.callback(
    Output("total-messages", "children"),
    Input("upload-chat", "contents"),
    State("upload-chat", "filename"),
    State("upload-chat", "last_modified")
)
def update_info_cards(contents, filename, last_modified):
    content_type, content_string = contents.split(",")
    decoded_text = b64decode(content_string).decode("utf-8")
    try:
        if "txt" in filename:
            chat = decoded_text.splitlines()
            chat = clearchat(chat)
            df = build_df(chat)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    df_c = df.copy()
    total_messages = len(df_c)
    return total_messages


if __name__ == "__main__":
    app.run_server(debug=True)
