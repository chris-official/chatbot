import os
import dash
from dash import html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from time import sleep
from itertools import chain, zip_longest
from datetime import datetime, timezone, timedelta
from bot import setup_agent, query_llm, check_open_ai_key
from prompts import PROMPT_EXAMPLES
from api import check_open_weather_key


# setup chatbot
agent, tools = setup_agent(model="gpt-4o-mini", temperature=0.5, verbose=False)

# check API keys
open_ai_is_valid = check_open_ai_key()
open_weather_is_valid = check_open_weather_key()
starting_mode = "offline" if not open_ai_is_valid or not open_weather_is_valid else "online"


def header(name: str, mode: str) -> dbc.Row:
    """Create the header of the website."""

    # Set the title
    title = html.H1(name, style={"margin-top": 5})

    # Offline mode switch
    switch = dbc.Checklist(
        options=[{"label": "Offline Mode", "value": 1}],
        value=[1] if mode == "offline" else [],
        id="offline-switch",
        switch=True,
    )

    # Theme selector switch
    select = dbc.Checklist(
        options=[{"label": "Dark Mode", "value": "dark"}],
        value=["dark"],
        id="theme-switch",
        switch=True,
    )

    # Return the header
    return dbc.Row([dbc.Col(title, md=8), dbc.Col([switch, select], md=4)])


def textbox(text: str, box: str = "ai") -> dbc.Card | html.Div:
    """Creates message boxes."""

    # Create the user message box
    if box == "user":
        return dbc.Card(text, body=True, inverse=True, className="user-message message-box")
    # Create the AI message box
    elif box == "ai":
        bot_img = html.Img(src=app.get_asset_url("bot.png"), className="thumbnail")
        card = dbc.Card(
            dcc.Markdown(text, className="mgs-text"), body=True, inverse=False, className="ai-message message-box"
        )
        return html.Div([bot_img, card])
    # Raise an error if the box type is not recognized
    else:
        raise ValueError(f"Received unknown message box type: {box} but expected 'user' or 'ai'.")


def weather_card(title: str, temp: str = "--", cloud: str = "--", wind: str = "--", rain: str = "--",
                 icon: str = "02d") -> dbc.Card:
    """Create a weather card for the forecast information column."""

    # Get the weather icon
    icon = html.Img(src=f"https://openweathermap.org/img/wn/{icon}@2x.png", className="weather-icons")

    # Fill and return the weather card
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
    """Update the display of the conversation."""

    # Combine the questions and answers
    history = [x for x in chain(*zip_longest(questions, answers)) if x is not None]

    # Create the initial message
    initial_msg = [textbox("Hi, my name is Sky! How can I help you?", box="ai")]

    # Create the message boxes
    messages = [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="ai")
        for i, x in enumerate(history)
    ]
    initial_msg.extend(messages)

    # Return the updated display
    return initial_msg


font = ("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;"
        "0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")

# Define app, themes, icons, fonts, and title
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA, dbc.icons.FONT_AWESOME, font])
app.title = "Weather Chatbot"
server = app.server


# Define the conversation display
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

# Define input controls
controls = dbc.InputGroup(
    [
        dbc.Textarea(id="user-input", placeholder="Write to the chatbot...", autofocus=True),
        dbc.Button(html.I(className="fas fa-paper-plane fa-lg"), id="submit"),
    ]
)

# Define the example buttons
buttons = html.Div(
    [
        dbc.Button(text, color="primary", id=f"example-button_{i}", className="example-buttons")
        for i, text in enumerate(PROMPT_EXAMPLES)
    ],
    className="d-grid gap-2 button-wrapper",
)

# Define the main app layout
app.layout = html.Div(
    dbc.Container(
        fluid=True,
        children=[
            html.Link(id='theme-css', rel='stylesheet', href='/assets/style.css'),
            header("Weather Chatbot", starting_mode),
            dbc.Alert(
                "The chatbot is running in Offline Mode!",
                color="warning",
                id="overlay-alert",
                is_open=True,
                duration=8000
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Examples"),
                            html.Div(
                                [
                                    html.Hr(),
                                    html.P("Click on any example to prefill the chatbox. Next, you can edit your \
                                    prompt or submit your question directly!"),
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
                                id="msg-spinner",
                            ),
                            controls,
                            dbc.Spinner(html.Div(id="loading-component"))
                        ],
                        className="chat-column"
                    ),
                    dbc.Col(
                        [
                            html.H2("7-Day Forecast"),
                            dbc.Tooltip(
                                "This column will update automatically once you submit a question.",
                                target="weather-cards-wrapper-id",
                                placement="left",
                                delay={"show": 300, "hide": 100},
                            ),
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
    [
        Output("weather-cards-wrapper-id", "children"),
        Output("location-name", "children")
    ],
    [Input("store-answers", "data")],
    [State("submit", "n_clicks")]
)
def update_weather_cards(answer_history, n_clicks):
    """Update the weather forecast cards."""

    # Define dates for next 7 days
    now = datetime.now(timezone(timedelta(hours=2)))
    dates = ["Today", "Tomorrow"]
    dates.extend([(now + timedelta(days=i)).strftime("%A") for i in range(2, 7)])

    # Get the location and weather data from api wrapper
    wrapper = tools[0].api_wrapper
    location_data = wrapper.location
    weather_data = wrapper.weather

    # Check if location data is available
    if (location_data is not None) and (answer_history != []):
        location = location_data["name"]
        if location_data.get("state") is not None:
            location += f", {location_data['state']}"
        location += f", {location_data['country']}"
    else:
        location = "No location set."

    # Return empty cards if no data is available
    if (n_clicks is None) or (weather_data is None):
        cards = [weather_card(day) for day in dates]
        return cards, location

    # Get the weather data
    daily = weather_data["daily"]

    # Get the icons
    icons = wrapper.get_icon_ids()

    # Fill the weather cards
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

    # Return the weather cards and location
    return cards, location


@callback(
    Output("user-input", "value", allow_duplicate=True),
    [Input(f"example-button_{i}", "n_clicks") for i in range(len(PROMPT_EXAMPLES))],
    [State(f"example-button_{i}", "children") for i in range(len(PROMPT_EXAMPLES))],
    prevent_initial_call=True
)
def on_button_click(*inputs):
    """Fill the chatbox with the example prompts."""

    # Get the triggered button id
    triggered_id = ctx.triggered_id
    n = int(triggered_id.split("_")[-1])

    # Get the index of the triggered button
    length = len(inputs) // 2
    idx = length + n

    # Return the example prompt of the triggered button
    return inputs[idx]


@callback(
    Output("display-conversation", "children"),
    [Input("store-questions", "data")],
    [State("store-answers", "data")],
)
def update_display_questions(questions, answers):
    """Update the display of the conversation when a new question is submitted."""
    return _update_display(questions, answers)


@callback(
    Output("display-conversation", "children", allow_duplicate=True),
    [Input("store-answers", "data")],
    [State("store-questions", "data")],
    prevent_initial_call=True
)
def update_display_answers(answers, questions):
    """Update the display of the conversation when a new answer is received."""
    return _update_display(questions, answers)


@callback(
    [
        Output("store-questions", "data"),
        Output("user-input", "value")
    ],
    [
        Input("submit", "n_clicks"),
        Input("user-input", "n_submit")
    ],
    [
        State("user-input", "value"),
        State("store-questions", "data")
    ],
)
def update_conversation(n_clicks, n_submit, user_input, question_history):
    """Update the conversation history with new questions."""

    # Return empty question history if no questions are submitted
    if n_clicks == 0:
        return [], ""

    # Return the old question history if empty input is submitted
    if user_input is None or user_input == "":
        return question_history, ""

    # Append the new question to the question history
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
        State("offline-switch", "value"),
    ],
)
def run_chatbot(n_clicks, n_submit, user_input, answer_history, offline_mode):
    """Runs the chatbot in online or offline mode and returns the answer history."""

    # Return old answer history if no questions are submitted
    if user_input is None or user_input == "":
        return answer_history

    # Return default message if chatbot is running in offline mode
    if len(offline_mode) == 1:
        sleep(1)
        answer_history.append("The weather is nice today!")
        return answer_history
    # Return warning message if OpenAI API key is missing
    elif not open_ai_is_valid:
        answer_history.append(
            "It seems that your OpenAI API key is missing. Please provide valid API keys to chat with the bot or \
            enable 'Offline Mode'."
        )
        return answer_history
    # Return warning message if OpenWeatherMap API key is missing
    elif not open_weather_is_valid:
        warning = ("It seems that your OpenWeatherMap API key is missing or invalid. "
                   "Please provide valid API keys to get real-time weather data.")
        # Try to query the chatbot without real-time weather data
        try:
            response = query_llm(agent, user_input)
        except Exception as e:
            response = str(e)
        # Append the response and warning message to the answer history
        res = f"{response}\n\n**Note:** {warning}"
        answer_history.append(res)
        return answer_history
    # Run the chatbot in online mode
    else:
        # Try to query the chatbot
        try:
            response = query_llm(agent, user_input)
        # Return error message if an exception occurs
        except Exception as e:
            response = f"**Oops! Something went wrong:** \n\n{e}"
        answer_history.append(response)
        return answer_history


@callback(
    Output('theme-css', 'href'),
    [Input('theme-switch', 'value')]
)
def update_theme(theme):
    """Update the theme of the website."""
    if "dark" in theme:
        return '/assets/dark_style.css'
    return '/assets/style.css'


@callback(
    [
        Output("overlay-alert", "is_open"),
        Output("overlay-alert", "children"),
        Output("overlay-alert", "color"),
    ],
    [Input("offline-switch", "value")],
)
def toggle_alert(offline_mode):
    """Toggle the alert message based on the offline switch."""
    if open_ai_is_valid and open_weather_is_valid:
        # Return warning message if chatbot is running in offline mode
        if len(offline_mode) == 1:
            msg = "The chatbot is running in Offline Mode!"
            color = "warning"
        # Return success message if chatbot is running in online mode
        else:
            msg = "The chatbot is running in Online Mode!"
            color = "success"
    # Return warning message if API keys are missing
    else:
        msg = "API keys are missing or invalid! Running in Offline Mode by default."
        color = "danger"
    return True, msg, color


if __name__ == "__main__":
    # Check if the app is deployed on render
    is_deployed = os.getenv("RENDER", False)
    # Run the server in live mode if deployed
    if is_deployed:
        port = int(os.getenv("PORT", 10000))
        host = str(os.getenv("HOST", "0.0.0.0"))
        app.run_server(debug=False, port=port, host=host)
    # Run the server in debug mode if deployed locally
    else:
        app.run_server(debug=True)
