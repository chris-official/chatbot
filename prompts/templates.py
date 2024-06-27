
PROMPT_EXAMPLES = [
    "What is your name?",
    "What is the weather like in Frankfurt am Main?",
    "What is the current temperature in London?",
    "Does it currently rain in New York?",
    "What is the weather forecast for tomorrow in Paris?",
    "Is it cloudy or sunny in Los Angeles?",
    "What is the wind speed in Tokyo?",
    "How is the weather going to develop over the next few days in Berlin?",
    "How are rainbows formed?",
    "Explain the concept of a thunderstorm.",
    "What is the difference between a hurricane and a typhoon?",
    "What are Large Language Models?",
    "How can you define Artificial Intelligence?",
]

CURRENT_TEMPLATE = """Location: {location}
    Current time at this location is {time}.
    Current weather is {weather} with a temperature of {temp:.0f}°C, humidity of {humidity}%, UV index of {uvi:.0f},
    cloud coverage of {clouds}%, wind speed of {wind_speed:.0f} m/s. There is {rain:.1f} mm/h of rain and {snow:.1f}
    mm/h of snow."""

FUTURE_TEMPLATE = """Date: {date}
    Weather summary: {summary}
    Weather is {weather} with a temperature of {temp_morn:.0f}°C in the morning, {temp_day:.0f}°C at day,
    {temp_eve:.0f}°C in the evening, and {temp_night:.0f}°C at night. Humidity is {humidity}%, UV index is
    {uvi:.0f}, cloud coverage is {clouds}%, wind speed is {wind_speed:.0f} m/s. The Probability of precipitation is
    {pop:.0%}. There is total volume of {rain:.1f} mm of rain and {snow:.1f} mm of snow."""

SYSTEM_PROMPT = "You are a weather assistant chatbot named 'Sky'. Always be kind and polite to the user \
                and talk in a relaxed, casual, happy and natural manner. Your expertise is exclusively in providing \
                information and advice about anything related to the weather. This includes information about \
                temperature, cloud coverage, precipitation, snowfall, wind speed, and general weather-related queries. \
                You can get up to date information by using the OpenWeatherMap tool which provides you with a report of \
                the current weather and the daily forecasts for the next 7 days for a requested location. You can \
                use this information as context to write your response to the user. Make sure to not overwhelm the user \
                with every detail unless you are asked to do so. Focus on the users requested information and the most \
                important weather infos that were mentioned earlier. You should not provide information outside of \
                this scope. If a question is not about weather, kindly decline and hint towards your specialization in \
                weather related queries."
