import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from time import sleep
from itertools import chain, zip_longest


def header(name, app):
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("weather-icon.png"), style={"float": "right", "height": 60, "margin-top": 5}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


def textbox(text, box="AI"):
    if box == "user":
        return dbc.Card(text, body=True, color="primary", inverse=True, className="user-message message-box")
    elif box == "AI":
        thumbnail = html.Img(src=app.get_asset_url("bot.png"), className="thumbnail")
        box = dbc.Card(text, body=True, color="light", inverse=False, className="ai-message message-box")
        return html.Div([thumbnail, box])
    else:
        raise ValueError("Incorrect option for box.")


def weather_card(title, temp, cloud, wind, rain):
    icon = html.Img(src=app.get_asset_url("weather-icon.png"), className="icons")
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(icon, width=3, xxl=2, className="icon-col"),
                            dbc.Col(
                                [
                                    html.H5(title, className="card-title"),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.I(className="fas fa-temperature-half mar"), width=1),
                                            dbc.Col(f"{temp}°C", width=5),
                                            dbc.Col(html.I(className="fas fa-cloud mar"), width=1),
                                            dbc.Col(f"{cloud}%", width=5),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(html.I(className="fas fa-wind mar"), width=1),
                                            dbc.Col(f"{wind} m/s", width=5),
                                            dbc.Col(html.I(className="fas fa-droplet mar"), width=1),
                                            dbc.Col(f"{rain} mm/h", width=5),
                                        ]
                                    )
                                ],
                                width=9,
                                xxl=10,
                            )
                        ]
                    )
                ]
            ),
        ],
        className="weather-card",
    )


def _update_display(questions, answers):
    history = [x for x in chain(*zip_longest(questions, answers)) if x is not None]
    out = [textbox("Hi, my name is Sky! How can I help you?", box="AI")]
    messages = [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(history)
    ]
    out.extend(messages)
    return out


# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA, dbc.icons.FONT_AWESOME])
# server = app.server


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
        dbc.Button(html.I(className="fas fa-paper-plane fa-lg", style={"margin-right": "5px"}), id="submit"),
    ]
)

buttons = html.Div(
    [
        dbc.Button(text, color="primary", id=f"example-button_{i}", className="example-buttons") for i, text in enumerate(PROMPT_EXAMPLES)
    ],
    className="d-grid gap-2 button-wrapper",
)

app.layout = dbc.Container(
    fluid=True,
    children=[
        header("Weather Chatbot", app),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Examples"),
                        html.Hr(),
                        html.P("Click on an example to prefill the chatbox. Next, you can edit your prompt or submit the question directly."),
                        html.Hr(),
                        buttons,
                        html.Div(id="example-output"),
                    ],
                    width=3
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
                    ]
                ),
                dbc.Col(
                    [
                        html.H2("7-Day Forecast"),
                        html.Hr(),
                        html.Div(
                            [
                                weather_card("Today", 20, 30, 5, 0.5),
                                weather_card("Tuesday", 22, 40, 6, 0.7),
                                weather_card("Wednesday", 18, 20, 4, 0.3),
                                weather_card("Thursday", 19, 25, 5, 0.4),
                                weather_card("Friday", 21, 35, 6, 0.6),
                                weather_card("Saturday", 23, 45, 7, 0.8),
                                weather_card("Sunday", 24, 50, 8, 1.0),
                            ],
                            className="weather-cards-wrapper"
                        )
                    ],
                    width=3
                ),
            ]
        )
    ]
)


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
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-answers", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, answer_history):
    if n_clicks == 0:
        return []

    if user_input is None or user_input == "":
        return answer_history

    sleep(1)
    answer_history.append("Here will be the AI response.")
    return answer_history


if __name__ == "__main__":
    app.run_server(debug=True)
