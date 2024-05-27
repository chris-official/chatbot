from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from weather_api import OpenWeatherMapAPIWrapper
from typing import Optional, Type


class OpenWeatherMapInput(BaseModel):
    city: str = Field(
        description="The city for which to fetch weather information as string e.g. 'London' or 'Berlin'."
    )
    country: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="The two letter country code for the city if applicable as string e.g. 'GB' or 'DE'."
    )
    state: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description="The two letter state code for the city if applicable as string e.g. 'NY'. Only for cities in the US."
    )


class OpenWeatherMapQuery(BaseTool):
    """Tool that queries the OpenWeatherMap API."""

    api_wrapper: OpenWeatherMapAPIWrapper = Field(default_factory=OpenWeatherMapAPIWrapper)

    name: str = "OpenWeatherMap"
    description: str = """A wrapper around OpenWeatherMap API.
    Useful for fetching current and future weather information for a specified location.
    Input must be at least a city string (e.g. 'London').
    To avoid ambiguity, in addition to the city, a two letter country code can be passed (e.g. 'London', 'GB').
    Additionally, only for the US a two letter state code can be passed (e.g. 'Ontario', 'US', 'NY')."""

    args_schema: Type[BaseModel] = OpenWeatherMapInput
    return_direct: bool = False

    def _run(self, city: str, country: Optional[str] = None, state: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the OpenWeatherMap tool."""
        return self.api_wrapper.get_weather(city, country, state)
