import re
import emoji
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
            name[-1] = "System Message"

    df = pd.DataFrame(list(zip(date_list, time, name, content)),
                      columns=["Date", "Time", "Name", "Content"])

    df_system = pd.DataFrame(columns=df.columns)
    cond = df.Name == "System Message"
    rows = df.loc[cond, :]
    df_system = df_system.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    return df, df_system


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
                dbc.CardHeader("TOTAL EMOJIS", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="total-emojis")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TOTAL LINKS", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="total-links")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TOTAL MEDIA", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="total-media")
                ], style={"textAlign": "center"})
            ])
        ], width=3)
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("TOTAL CHATTERS", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="total-chatters")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("MOST USED EMOJI", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="most-used-emoji")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("PERSON WITH MOST MESSAGES", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="most-messages")
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


@ app.callback(
    Output("total-messages", "children"),
    Output("total-chatters", "children"),
    Output("total-emojis", "children"),
    Output("word-cloud", "figure"),
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
            df, df_system = build_df(chat)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    df_c = df.copy()

    total_messages = len(df_c)

    total_chatters = len(df_c["Name"].unique())
    print(df_c.Content.astype(str))
    # figure = px.line(df_c, x=
    # slow as fuck 6-7s
    # it's actually total messages that have emojis (meaning a message like "👽👽👽👽😂👽" would only count as 1)
    # come back to this later, don't forget to return the right thing
    # emojilist = df_c["Content"].str.extract(emoji.get_emoji_regexp()).dropna()

    wordcloud = WordCloud(background_color="white", min_word_length=4, width=800, height=400).generate(
        " ".join(df_c.Content.astype(str)))
    fig_wordcloud = px.imshow(
        wordcloud, template="ggplot2", title="Messages Wordcloud")
    fig_wordcloud.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    fig_wordcloud.update_xaxes(visible=False)
    fig_wordcloud.update_yaxes(visible=False)

    return total_messages, total_chatters, 1, fig_wordcloud


if __name__ == "__main__":
    app.run_server(debug=True)
