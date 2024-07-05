import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from prompts import CURRENT_TEMPLATE, FUTURE_TEMPLATE

load_dotenv()


class OpenWeatherMapAPIWrapper:
    """Wrapper class for OpenWeatherMap API."""
    def __init__(self):
        self.key = os.getenv("OPENWEATHERMAP_API_KEY", "")
        self.current_template = CURRENT_TEMPLATE
        self.future_template = FUTURE_TEMPLATE
        self.location = None
        self.weather = None

    def get_location(self, city_name: str, country: str = None, state: str = None) -> dict | str:
        """Get location information from OpenWeatherMap API."""

        # prepare location string
        location = city_name
        if state and (country == "US"):
            location += f",{state}"
        if country:
            location += f",{country}"

        # prepare request parameters
        params = {
            "q": location,
            "limit": 1,
            "appid": self.key
        }

        # request location information
        response = requests.get("https://api.openweathermap.org/geo/1.0/direct", params=params)

        # handle response
        response = self.handle_response(response)
        if isinstance(response, str):
            return f"Could not get location because of following error: {response}"
        loc = response[0]
        _ = loc.pop("local_names", None)
        return loc

    def get_weather(self, city_name: str, country: str = None, state: str = None) -> str:
        """Get weather information from OpenWeatherMap API."""

        # get location information
        self.location = self.get_location(city_name, country, state)
        if isinstance(self.location, str):
            return f"Could not get location because of following error: {self.location}"

        # prepare request parameters
        params = {
            "lat": self.location["lat"],
            "lon": self.location["lon"],
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "appid": self.key
        }

        # request weather information
        self.weather = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=params)

        # handle response
        self.weather = self.handle_response(self.weather)
        if isinstance(self.weather, str):
            return f"Could not get weather because of following error: {self.weather}"

        # format templates and return output
        return self.get_output()

    def get_output(self) -> str:
        """Create output string for weather information"""

        # prepare location string
        loc = self.location["name"]
        if self.location["country"] == "US":
            loc += f", {self.location['state']}"
        loc += f", {self.location['country']}"

        # get current and forecast data
        current = self.weather["current"]
        forecast = self.weather["daily"]

        # extract rain data
        rain = current.get("rain", 0)
        rain = rain if isinstance(rain, int) else rain.get("1h", 0)

        # extract snow data
        snow = current.get("snow", 0)
        snow = snow if isinstance(snow, int) else snow.get("1h", 0)

        # format current weather information template
        weather_current = self.current_template.format(
            location=loc,
            time=datetime.fromtimestamp(current["dt"] + self.weather["timezone_offset"], timezone.utc).strftime('%A %Y-%m-%d %H:%M'),
            temp=current["temp"],
            humidity=current["humidity"],
            uvi=current["uvi"],
            clouds=current["clouds"],
            wind_speed=current["wind_speed"],
            rain=rain,
            snow=snow,
            weather=current["weather"][0]["description"]
        )

        # format forecast weather information templates
        weather_forecasts = [self.future_template.format(
            location=loc,
            date=datetime.fromtimestamp(data["dt"] + self.weather["timezone_offset"], timezone.utc).strftime('%A %Y-%m-%d'),
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

        # join current and forecast weather information
        weather_forecast = "\n####\n".join(weather_forecasts)

        # return context string
        return f"{weather_current}\n####\n{weather_forecast}"

    def get_icon_ids(self) -> list[str]:
        """Get icon ids for weather forecast column."""
        icon_ids = [data["weather"][0]["icon"] for data in self.weather["daily"]]
        return icon_ids

    @staticmethod
    def handle_response(response) -> dict | str:
        """Handle response from OpenWeatherMap API."""
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


def check_open_weather_key() -> bool:
    """Check if OpenWeatherMap API key is valid."""
    open_weather = os.getenv("OPENWEATHERMAP_API_KEY", "")
    if len(open_weather) < 16:
        return False
    return True
