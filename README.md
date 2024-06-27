# Chatbot

## Description

This is a weather chatbot that uses the [langchain](https://python.langchain.com/v0.2/docs/introduction/) library
and [OpenWeatherMap](https://openweathermap.org/api) API to generate responses to weather-related user queries. A
user interface is provided by a [dash](https://dash.plotly.com/tutorial) web application that allows users to chat with the chatbot.

## Installation

### 1. Visit online chatbot (no installation required)

You can visit the online chatbot [here](https://chatbot-weather.herokuapp.com/).

### 2. Run the chatbot locally (requires installation)

Create a new virtual environment and install the dependencies:
    
```bash
python -m venv chatbot_env  # Create a new virtual environment
chatbot_env/Scripts/activate.bat  # Activate the virtual environment
```

Copy the contents of the chatbot folder into the virtual environment directory and install the dependencies:

```bash
pip install -r requirements.txt  # Install the dependencies
```

Open the .env file and add your OpenAI and OpenWeatherMap API key.

```bash
OPENAI_API_KEY="your_openai_api_key"
OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"
```

> [!WARNING]
> When no API keys are provided, the chatbot will run in offline mode and will not make any API calls.
> Instead, it will output a default response.

## Usage

To run the chatbot, execute the following command:

```bash
python app.py
```

This will start a local server on `http://localhost:5000/`.
Just open this URL in your browser to start chatting with the chatbot.
