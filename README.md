# Chatbot

## Description

This is a weather chatbot that uses the [langchain](https://python.langchain.com/v0.2/docs/introduction/) library
and [OpenWeatherMap](https://openweathermap.org/api) API to generate responses to weather-related user queries. A
user interface is provided by a [dash](https://dash.plotly.com/tutorial) web application that allows users to chat with the chatbot.

## Installation

### Visit online chatbot - no installation required (recommended)

You can visit the online chatbot [here](https://chatbot-weather.herokuapp.com/).

### Run the chatbot locally - requires manual installation

Create a new virtual environment and activate it:
    
```bash
python -m venv chatbot_env  # Create a new virtual environment
chatbot_env/Scripts/activate.bat  # Activate the virtual environment
```

Copy the contents of the chatbot folder into the virtual environment directory and install the dependencies:

```bash
pip install -r requirements.txt  # Install the dependencies
```

Open the .env file and add your OpenAI and OpenWeatherMap API key. You can get your OpenAI key
[here](https://platform.openai.com/api-keys) and your OpenWeatherMap key
[here](https://home.openweathermap.org/api_keys). Finally, the file should look like this:

```bash
OPENAI_API_KEY="your_openai_api_key"
OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"
```

> [!WARNING]
> When no API keys are provided, the chatbot will run in offline mode and will not make any API calls.
> Instead, it will output a default response.

## Usage

To run the chatbot interface on your machine, execute the following command:

```bash
python app.py
```

This will start a local server on [`http://127.0.0.1:8050`](http://127.0.0.1:8050).
Just open this URL in your browser to start chatting with the chatbot locally.
