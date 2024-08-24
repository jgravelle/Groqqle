# tools/web_tools/Weather_US_Tool.py

# Fetches weather information for a given US city or city/state combination.

import os
import sys
import requests
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.Base_Tool import Base_Tool
DEBUG = os.environ.get('DEBUG') == 'True'

class Weather_US_Tool(Base_Tool):
    BASE_URL = "https://weathermateplus.com/api/location/"

    def execute(self, address: str) -> Dict[str, Any]:
        """
        Fetches weather information for a given US city or city/state combination.

        Args:
        address (str): The city or city/state combination to fetch weather for.

        Returns:
        Dict[str, Any]: A dictionary containing the weather information or an error message.
        """
        try:
            encoded_address = quote_plus(address)
            url = f"{self.BASE_URL}?address={encoded_address}"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            return self._format_output(self._extract_relevant_data(data))
        except requests.RequestException as e:
            return self._handle_error(f"Error fetching weather data: {str(e)}")
        except KeyError as e:
            return self._handle_error(f"Error parsing weather data: {str(e)}")

    def _validate_input(self, data: Dict[str, str]) -> Optional[str]:
        if 'address' not in data:
            return "Address is required."
        if not isinstance(data['address'], str):
            return "Address must be a string."
        return None

    def _extract_relevant_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "location": data["location"],
            "currentObservation": data["currentObservation"],
            "day1": data["days"][0] if data["days"] else None
        }

    def _format_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        formatted = {
            "location": result["location"]["areaDescription"],
            "current": {
                "temperature": result["currentObservation"]["temperature"],
                "weather": result["currentObservation"]["weather"],
                "windSpeed": result["currentObservation"]["windSpeed"],
                "windDirection": result["currentObservation"]["windDirection"],
            },
            "forecast": {}
        }

        if result["day1"]:
            formatted["forecast"] = {
                "temperature": result["day1"]["temperature"],
                "shortForecast": result["day1"]["shortForecast"],
                "windSpeed": result["day1"]["windSpeed"],
                "windDirection": result["day1"]["windDirection"],
                "precipitationProbability": result["day1"]["probabilityOfPrecipitation"],
            }

        return formatted

    def _handle_error(self, error_message: str) -> Dict[str, str]:
        if DEBUG:
            print(f"Weather_US_Tool error: {error_message}")
        return {"error": error_message, "status": "error"}

if __name__ == "__main__":
    tool = Weather_US_Tool()
    address = input("Enter a US city or city, state: ")
    result = tool.execute(address)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Weather for {result['location']}:")
        print(f"Current: {result['current']['temperature']}°F, {result['current']['weather']}")
        print(f"Wind: {result['current']['windSpeed']} mph {result['current']['windDirection']}")
        print("\nForecast:")
        print(f"Temperature: {result['forecast']['temperature']}°F")
        print(f"Conditions: {result['forecast']['shortForecast']}")
        print(f"Wind: {result['forecast']['windSpeed']} {result['forecast']['windDirection']}")
        print(f"Precipitation Probability: {result['forecast']['precipitationProbability']}")