import os
import dash
from dash import html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from time import sleep
from itertools import chain, zip_longest
from datetime import datetime, timezone, timedelta
from bot import setup_agent, query_llm
from prompts import PROMPT_EXAMPLES

# robot: https://cdn-icons-png.flaticon.com/512/3398/3398643.png

# setup chatbot
agent, tools = setup_agent(model="gpt-3.5-turbo", temperature=0.5, verbose=False)


def header(name: str) -> dbc.Row:
    title = html.H1(name, style={"margin-top": 5})
    switch = dbc.Checklist(
        options=[{"label": "Debug Mode", "value": 1}],
        value=[],
        id="debug-switch",
        switch=True,
    )
    select = dbc.Checklist(
        options=[{"label": "Dark Mode", "value": "dark"}],
        value=["dark"],
        id="theme-switch",
        switch=True,
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col([switch, select], md=4)])


def textbox(text: str, box: str = "ai") -> dbc.Card | html.Div:
    if box == "user":
        return dbc.Card(text, body=True, inverse=True, className="user-message message-box")
    elif box == "ai":
        thumbnail = html.Img(src=app.get_asset_url("bot.png"), className="thumbnail")
        box = dbc.Card(text, body=True, inverse=False, className="ai-message message-box")
        return html.Div([thumbnail, box])
    else:
        raise ValueError("Incorrect option for box.")


def weather_card(title: str, temp: str = "--", cloud: str = "--", wind: str = "--", rain: str = "--", icon: str = "02d") -> dbc.Card:
    icon = html.Img(src=f"https://openweathermap.org/img/wn/{icon}@2x.png", className="weather-icons")
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(icon, width=3, className="icon-col"),
                            dbc.Col(
                                [
                                    html.H5(title, className="card-title"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.I(className="fas fa-temperature-half small-icons"),
                                                    f"{temp} °C"
                                                ],
                                                width=6
                                            ),
                                            dbc.Col(
                                                [
                                                    html.I(className="fas fa-cloud small-icons"),
                                                    f"{cloud} %"
                                                ],
                                                width=6
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.I(className="fas fa-droplet small-icons"),
                                                    f"{rain} mm"
                                                ],
                                                width=6
                                            ),
                                            dbc.Col(
                                                [
                                                    html.I(className="fas fa-wind small-icons"),
                                                    f"{wind} m/s"
                                                ],
                                                width=6
                                            ),
                                        ]
                                    )
                                ],
                                width=9,
                            )
                        ]
                    )
                ]
            ),
        ],
        className="weather-card",
    )


def _update_display(questions: list, answers: list) -> list:
    history = [x for x in chain(*zip_longest(questions, answers)) if x is not None]
    out = [textbox("Hi, my name is Sky! How can I help you?", box="ai")]
    messages = [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="ai")
        for i, x in enumerate(history)
    ]
    out.extend(messages)
    return out


font = ("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;"
        "0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")

# Define app, themes, icons, fonts, and title
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA, dbc.icons.FONT_AWESOME, font])
app.title = "Weather Chatbot"
server = app.server


# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 120px)",
        "flex-direction": "column-reverse",
        "padding-top": "5px",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Textarea(id="user-input", placeholder="Write to the chatbot...", autofocus=True),
        dbc.Button(html.I(className="fas fa-paper-plane fa-lg"), id="submit"),
    ]
)

buttons = html.Div(
    [
        dbc.Button(text, color="primary", id=f"example-button_{i}", className="example-buttons") for i, text in enumerate(PROMPT_EXAMPLES)
    ],
    className="d-grid gap-2 button-wrapper",
)

app.layout = html.Div(
    dbc.Container(
        fluid=True,
        children=[
            html.Link(id='theme-css', rel='stylesheet', href='/assets/style.css'),
            header("Weather Chatbot"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Examples"),
                            html.Div(
                                [
                                    html.Hr(),
                                    html.P("Click on any example to prefill the chatbox. Next, you can edit your prompt or submit your question directly!"),
                                    html.Hr(),
                                ],
                                className="button-hint"
                            ),
                            buttons,
                        ],
                        width=3,
                        className="button-column"
                    ),
                    dbc.Col(
                        [
                            dcc.Store(id="store-questions", data=[], storage_type="memory"),
                            conversation,
                            dbc.Spinner(
                                dcc.Store(id="store-answers", data=[], storage_type="memory"),
                                color="secondary",
                                spinner_style={"position": "absolute", "bottom": "10px", "left": "5px"},
                            ),
                            controls,
                            dbc.Spinner(html.Div(id="loading-component"))
                        ],
                        className="chat-column"
                    ),
                    dbc.Col(
                        [
                            html.H2("7-Day Forecast"),
                            html.Hr(),
                            html.Div(
                                [
                                    html.I(className="fas fa-location-dot small-icons"),
                                    html.Span(id="location-name")
                                ],
                                className="location"
                            ),
                            html.Div(className="weather-cards-wrapper", id="weather-cards-wrapper-id"),
                        ],
                        width=3,
                        className="forecast-column"
                    ),
                ]
            )
        ]
    ),
    id="main-container"
)


@callback(
    [Output("weather-cards-wrapper-id", "children"), Output("location-name", "children")],
    [Input("store-answers", "data")],
    [State("submit", "n_clicks")]
)
def update_weather_cards(answer_history, n_clicks):
    now = datetime.now(timezone(timedelta(hours=2)))
    dates = ["Today", "Tomorrow"]
    dates.extend([(now + timedelta(days=i)).strftime("%A") for i in range(2, 7)])

    wrapper = tools[0].api_wrapper
    location_data = wrapper.location
    weather_data = wrapper.weather

    if (location_data is not None) and (answer_history != []):
        location = location_data["name"]
        if location_data.get("state") is not None:
            location += f", {location_data['state']}"
        location += f", {location_data['country']}"
    else:
        location = "No location set."

    if (n_clicks is None) or (weather_data is None):
        cards = [weather_card(day) for day in dates]
        return cards, location

    daily = weather_data["daily"]
    icons = wrapper.get_icon_ids()
    cards = [
        weather_card(
            day,
            round(data["temp"]["day"]),
            round(data["clouds"]),
            round(data["wind_speed"]),
            round(data.get("rain", 0.0), 1),
            icon
        )
        for day, data, icon in zip(dates, daily, icons)
    ]
    return cards, location


@callback(
    Output("user-input", "value", allow_duplicate=True),
    [Input(f"example-button_{i}", "n_clicks") for i in range(len(PROMPT_EXAMPLES))],
    [State(f"example-button_{i}", "children") for i in range(len(PROMPT_EXAMPLES))],
    prevent_initial_call=True
)
def on_button_click(*inputs):
    triggered_id = ctx.triggered_id
    n = int(triggered_id.split("_")[-1])
    length = len(inputs) // 2
    idx = length + n
    return inputs[idx]


@callback(
    Output("display-conversation", "children"),
    [Input("store-questions", "data")],
    [State("store-answers", "data")],
)
def update_display_questions(questions, answers):
    return _update_display(questions, answers)


@callback(
    Output("display-conversation", "children", allow_duplicate=True),
    [Input("store-answers", "data")],
    [State("store-questions", "data")],
    prevent_initial_call=True
)
def update_display_answers(answers, questions):
    return _update_display(questions, answers)


@callback(
    [Output("store-questions", "data"), Output("user-input", "value")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-questions", "data")],
)
def update_conversation(n_clicks, n_submit, user_input, question_history):
    if n_clicks == 0:
        return [], ""

    if user_input is None or user_input == "":
        return question_history, ""

    question_history.append(user_input)
    return question_history, ""


@callback(
    Output("store-answers", "data"),
    [
        Input("submit", "n_clicks"),
        Input("user-input", "n_submit")
    ],
    [
        State("user-input", "value"),
        State("store-answers", "data"),
        State("debug-switch", "value"),
    ],
)
def run_chatbot(n_clicks, n_submit, user_input, answer_history, debug_mode):
    if user_input is None or user_input == "":
        return answer_history

    if len(debug_mode) == 1:
        sleep(1)
        answer_history.append("The weather is nice today! Please provide valid API keys to get real weather data.")
        return answer_history
    else:
        response = query_llm(agent, user_input)
        answer_history.append(response)
        return answer_history


@app.callback(
    Output('theme-css', 'href'),
    [Input('theme-switch', 'value')]
)
def update_theme(theme):
    if "dark" in theme:
        return '/assets/dark_style.css'
    return '/assets/style.css'


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    host = str(os.getenv("HOST", "127.0.0.1"))
    app.run_server(debug=False, port=port, host=host)
