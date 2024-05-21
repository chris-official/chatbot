import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import requests

load_dotenv()


class OpenWeatherMapAPIWrapper:
    def __init__(self):
        self.key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.current_template = """Location: {location}
        Current time at this location is {time}.
        Current weather is {weather} with a temperature of {temp}°C, humidity of {humidity}%, UV index of {uvi}, cloud 
        coverage of {clouds}%, wind speed of {wind_speed} m/s. There is {rain}mm/h of rain and {snow}mm/h of snow."""
        self.future_template = """Date: {date}
        Weather summary: {summary}
        Weather is {weather} with a temperature of {temp_morn}°C in the morning, {temp_day}°C at day, {temp_eve}°C in 
        the evening, and {temp_night}°C at night. Humidity is {humidity}%, UV index is {uvi}, cloud 
        coverage is {clouds}%, wind speed is {wind_speed} m/s. The Probability of precipitation is {pop:.0%}. 
        There is total volume of {rain}mm of rain and {snow}mm of snow."""

    def get_location(self, city_name: str, country: str = None, state: str = None) -> dict:
        location = city_name
        if country:
            location += f",{country}"
        if state:
            location += f",{state}"

        params = {
            "q": location,
            "limit": 1,
            "appid": self.key
        }

        response = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=params)
        response = self.handle_response(response)
        if isinstance(response, str):
            return f"Could not get location because of following error: {response}"
        loc = response[0]
        _ = loc.pop("local_names", None)
        return loc

    def get_weather(self, city_name: str, country: str = None, state: str = None) -> str:
        location = self.get_location(city_name, country, state)
        params = {
            "lat": location["lat"],
            "lon": location["lon"],
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "appid": self.key
        }

        response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=params)
        response = self.handle_response(response)
        if isinstance(response, str):
            return f"Could not get weather because of following error: {response}"

        return self.format_output(location, response)

    def format_output(self, location: dict, response: dict) -> str:

        loc = location["name"]
        if location["country"] == "US":
            loc += f", {location['state']}"
        loc += f", {location['country']}"

        current = response["current"]
        forecast = response["daily"]

        rain = current.get("rain", 0)
        rain = rain if isinstance(rain, int) else rain.get("1h", 0)

        snow = current.get("snow", 0)
        snow = snow if isinstance(snow, int) else snow.get("1h", 0)

        weather_current = self.current_template.format(
            location=loc,
            time=datetime.fromtimestamp(current["dt"] + response["timezone_offset"], timezone.utc).strftime('%Y-%m-%d %H:%M'),
            temp=current["temp"],
            humidity=current["humidity"],
            uvi=current["uvi"],
            clouds=current["clouds"],
            wind_speed=current["wind_speed"],
            rain=rain,
            snow=snow,
            weather=current["weather"][0]["description"]
        )

        weather_forecasts = [self.future_template.format(
            location=loc,
            date=datetime.fromtimestamp(data["dt"] + response["timezone_offset"], timezone.utc).strftime('%Y-%m-%d'),
            summary=data["summary"],
            temp_morn=data["temp"]["morn"],
            temp_day=data["temp"]["day"],
            temp_eve=data["temp"]["eve"],
            temp_night=data["temp"]["night"],
            humidity=data["humidity"],
            uvi=data["uvi"],
            clouds=data["clouds"],
            wind_speed=data["wind_speed"],
            pop=data["pop"],
            rain=data.get("rain", 0),
            snow=data.get("snow", 0),
            weather=data["weather"][0]["description"]
        ) for data in forecast[1:]]

        weather_forecast = "\n####\n".join(weather_forecasts)

        return f"{weather_current}\n####\n{weather_forecast}"

    @staticmethod
    def handle_response(response):
        match response.status_code:
            case 200:
                return response.json()
            case 400:
                return "400 Bad Request"
            case 401:
                return "401 Unauthorized"
            case 404:
                return "404 Not Found"
            case 429:
                return "429 Too Many Requests"
            case _:
                return f"{response.status_code} Unexpected Error"