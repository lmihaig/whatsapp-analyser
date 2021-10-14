import re
from datetime import date
from base64 import b64decode
import dash
import diskcache
from dash import dcc, html
from dash.long_callback import DiskcacheLongCallbackManager
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import emoji


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
            content.append(text.split("-")[1])
            name[-1] = "System Message"

    df = pd.DataFrame(list(zip(date_list, time, name, content)),
                      columns=["Date", "Time", "Name", "Content"])

    df_system = pd.DataFrame(columns=df.columns)
    cond = df["Name"] == "System Message"
    rows = df.loc[cond, :]
    df_system = df_system.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    df_media = pd.DataFrame(columns=df.columns)
    cond = df["Content"] == " <Media omitted>"
    rows = df.loc[cond, :]
    df_media = df_media.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    df_links = pd.DataFrame(columns=df.columns)
    # sorry if someone was having a discussion about https or http
    rows = df[df["Content"].astype(str).str.contains("https|http")]
    df_links = df_links.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    df = df.reset_index()
    return df, df_system, df_media, df_links


# DARKLY, SLATE, SUPERHERO
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], meta_tags=[
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
        ], width=2),
        dbc.Col([

        ], width=1),
        dbc.Col([
            dcc.Upload([
                'Drag and Drop or ',
                html.A('Select a File')], className="align-items-center", id="upload-chat",
                style={
                "display": "inline-block",
                "text-align": "center",
                "font-size": "11px",
                "font-weight": "600",
                "line-height": "38px",
                "letter-spacing": ".1rem",
                "text-transform": "uppercase",
                "text-decoration": "none",
                "white-space": "nowrap",
                "background-color": "transparent",
                "border-radius": "4px",
                "border": "1px",
                "cursor": "pointer",
                "box-sizing": "border-box",
                'width': '95%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
            })])
    ], className="mt-2 mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Input(id="queryword", placeholder="Word to search for"),
        ]),
        dbc.Col([
            dbc.Button('Analyse', id='submit-val', n_clicks=0, block=True,
                       style={
                           "color":  "#00BC8C",
                           "border-style": "solid",
                           "border-width": "1px",
                           "border-color":  "#00BC8C",
                           "border-radius": "10px"
                       })
        ])
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
                    html.H2(id="most-messages-person")
                ], style={"textAlign": "center"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("DAY WITH MOST MESSAGES", style={
                               "textAlign": "center"}),
                dbc.CardBody([
                    html.H2(id="most-messages-day")
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
    Output("total-emojis", "children"),
    Output("total-links", "children"),
    Output("total-media", "children"),
    Output("total-chatters", "children"),
    Output("most-used-emoji", "children"),
    Output("most-messages-person", "children"),
    Output("most-messages-day", "children"),
    Output("line-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("word-cloud", "figure"),
    Input("submit-val", "n_clicks"),
    State("queryword", "value"),
    State("upload-chat", "contents"),
    State("upload-chat", "filename"),
    State("upload-chat", "last_modified"),
)
def update_cards(click, queryword, contents, filename, last_modified):
    content_type, content_string = contents.split(",")
    decoded_text = b64decode(content_string).decode("utf-8")
    try:
        if "txt" in filename:
            chat = decoded_text.splitlines()
            chat = clearchat(chat)
            df, df_system, df_media, df_links = build_df(chat)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # total non-link non-media non-system messages
    total_messages = len(df)

    # all the people that have ever sent a message in this chat
    total_chatters = len(df["Name"].unique())

    # figure = px.line(df_c, x=
    # slow as fuck 6-7s
    # it's actually total messages that have emojis (meaning a message like "👽👽👽👽😂👽" would only count as 1)
    # come back to this later, don't forget to return the right thing
    # emojilist = df_c["Content"].str.extract(emoji.get_emoji_regexp()).dropna()

    wordcloud = WordCloud(background_color="rgb(48,48,48)", min_word_length=4, width=800, height=400).generate(
        " ".join(df["Content"].astype(str)))
    fig_wordcloud = px.imshow(
        wordcloud, template="plotly_dark", title="Messages Wordcloud")
    fig_wordcloud.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
    fig_wordcloud.update_xaxes(visible=False)
    fig_wordcloud.update_yaxes(visible=False)

    return total_messages, 1, 1, 1, total_chatters, 1, 1, 1, 1, 1, 1, fig_wordcloud
    # return total_messages, total_emojis, total_links, total_media, total_chatters, most_used_emoji, most_messages_person, most_messages_day, fig_linechart, fig_piechart, fig_barchart, fig_wordcloud


if __name__ == "__main__":
    app.run_server(debug=True)
