import os
import requests
from datetime import datetime, timezone


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
        self.location = None
        self.weather = None

    def get_location(self, city_name: str, country: str = None, state: str = None) -> dict | str:
        location = city_name
        if state and (country == "US"):
            location += f",{state}"
        if country:
            location += f",{country}"

        params = {
            "q": location,
            "limit": 1,
            "appid": self.key
        }

        response = requests.get("https://api.openweathermap.org/geo/1.0/direct", params=params)
        response = self.handle_response(response)
        if isinstance(response, str):
            return f"Could not get location because of following error: {response}"
        loc = response[0]
        _ = loc.pop("local_names", None)
        return loc

    def get_weather(self, city_name: str, country: str = None, state: str = None) -> str:
        self.location = self.get_location(city_name, country, state)
        if isinstance(self.location, str):
            return f"Could not get location because of following error: {self.location}"

        params = {
            "lat": self.location["lat"],
            "lon": self.location["lon"],
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "appid": self.key
        }

        self.weather = requests.get("https://api.openweathermap.org/data/3.0/onecall", params=params)
        self.weather = self.handle_response(self.weather)
        if isinstance(self.weather, str):
            return f"Could not get weather because of following error: {self.weather}"

        return self.get_output()

    def get_output(self) -> str:

        loc = self.location["name"]
        if self.location["country"] == "US":
            loc += f", {self.location['state']}"
        loc += f", {self.location['country']}"

        current = self.weather["current"]
        forecast = self.weather["daily"]

        rain = current.get("rain", 0)
        rain = rain if isinstance(rain, int) else rain.get("1h", 0)

        snow = current.get("snow", 0)
        snow = snow if isinstance(snow, int) else snow.get("1h", 0)

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

        weather_forecast = "\n####\n".join(weather_forecasts)

        return f"{weather_current}\n####\n{weather_forecast}"

    def get_icon_ids(self) -> list[str]:
        icon_ids = [data["weather"][0]["icon"] for data in self.weather["daily"]]
        return icon_ids

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
