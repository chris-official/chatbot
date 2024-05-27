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
    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        thumbnail = html.Img(
            src=app.get_asset_url("bot.png"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )
        box = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([thumbnail, box])

    else:
        raise ValueError("Incorrect option for `box`.")


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
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
        "padding-top": "5px",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.Button("Submit", id="submit"),
    ]
)

app.layout = dbc.Container(
    fluid=False,
    children=[
        header("Weather Chatbot", app),
        html.Hr(),
        dcc.Store(id="store-questions", data=[], storage_type="memory"),
        conversation,
        dbc.Spinner(
            dcc.Store(id="store-answers", data=[], storage_type="memory"),
            color="primary",
            spinner_style={"position": "absolute", "bottom": "25px"},
        ),
        controls,
        dbc.Spinner(html.Div(id="loading-component")),
    ],
)


@callback(
    Output("display-conversation", "children"),
    [Input("store-questions", "data")],
    [State("store-answers", "data")],
)
def update_display_questions(questions, answers):
    print("Updating display questions")
    return _update_display(questions, answers)


@callback(
    Output("display-conversation", "children", allow_duplicate=True),
    [Input("store-answers", "data")],
    [State("store-questions", "data")],
    prevent_initial_call=True
)
def update_display_answers(answers, questions):
    print("Updating display answers")
    return _update_display(questions, answers)


@callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@callback(
    Output("store-answers", "data"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-answers", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, answer_history):
    print("Running chatbot")
    if n_clicks == 0:
        return []

    if user_input is None or user_input == "":
        return answer_history

    sleep(3)
    answer_history.append("Here will be the AI response.")
    return answer_history


if __name__ == "__main__":
    app.run_server(debug=True)
