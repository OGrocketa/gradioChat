import os
import requests
from crewai.tools import tool

@tool("Google Geocoding Tool")
def google_geocoding_tool(address: str) -> str:
    """
    Tool to transform users query: {input} to the coordinates and typeOfPlace
    """
    api_key = os.environ["GOOGLE_PLACES_API_KEY"]
    url = "https://maps.googleapis.com/maps/api/geocode/json"

    params = {
        "address":address,
        "key": api_key,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        result = response.json()
        if result["results"]:
            coordinates = result["results"][0]["geometry"]["location"]
            return coordinates
    else:
        return {"error": response.status_code, "message": response.text}