# Weather Chatbot

## Description

This is a weather chatbot that uses the [Langchain](https://python.langchain.com/v0.2/docs/introduction/) library, the
[OpenAI](https://platform.openai.com/docs/api-reference/introduction) API and the
[OpenWeatherMap](https://openweathermap.org/api) API to generate responses to weather-related user queries. A user
interface is provided by a [Dash](https://dash.plotly.com/tutorial) web application that allows users to chat with the
chatbot intuitively without any manual installations. The chatbot has been deployed on [Render](https://render.com/)
and can be accessed online by visiting [iu-weather-chatbot.onrender.com](https://iu-weather-chatbot.onrender.com).

## Web UI (recommended)

No manual installation is required, and you can start chatting immediately! <br>
You can visit the online chatbot here: [iu-weather-chatbot.onrender.com](https://iu-weather-chatbot.onrender.com)

> [!NOTE]
> When accessing the online chatbot after a longer period of inactivity, you may need to wait a few seconds for the
> server to start up. Therefore, please be patient and wait for the website to load.

> [!TIP]
> For the best experience, use the chatbot on a desktop or laptop. Even though the chatbot is mobile-friendly,
> the UI is optimized for larger screens and some features are disabled to fit the smaller screen size.

## Manual Installation

Create a new virtual environment and activate it:
    
```bash
python -m venv chatbot_env
chatbot_env/Scripts/activate.bat
```

Copy the contents of the chatbot repository into the virtual environment directory and install the required dependencies:

```bash
pip install -r requirements.txt
```

Open the `.env` file and add your OpenAI and OpenWeatherMap API key. You can get your OpenAI key
[here](https://platform.openai.com/api-keys) and your OpenWeatherMap key
[here](https://home.openweathermap.org/api_keys). Finally, the file should look like this:

```bash
OPENAI_API_KEY="your_openai_api_key"
OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"
```

> [!WARNING]
> When no API keys are provided, the chatbot will run in offline mode and will not make any API calls.
> Instead, a default response will be displayed. For the chatbot to work properly, you must provide the API keys or
> visit the online chatbot.

## Usage

To start the chatbot interface on your machine, run `app.py` by executing the following command:

```bash
python app.py
```

This will initiate a local server at [`http://127.0.0.1:8050`](http://127.0.0.1:8050).
To start chatting with the chatbot, simply open this URL in your browser.