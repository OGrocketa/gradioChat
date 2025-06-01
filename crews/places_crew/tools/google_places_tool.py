import requests
import os
from crewai.tools import tool


@tool("Google Places Nearby Search")
def google_places_tool(latitude: float, longitude: float, typeOfPlace: str) -> str:
    """
    Returns nearby places of a specific type using Google Places API, near the area provided by the user

    Args:
        latitude (float): Latitude of the location
        longitude (float): Longitude of the location
        typeOfPlace (str): Type of place to search for (e.g., 'restaurant', 'museum')

    Returns:
        str: JSON string of the API result or error message.
    """
    api_key = os.environ["GOOGLE_PLACES_API_KEY"]
    nearby_search_url = "https://places.googleapis.com/v1/places:searchNearby"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.googleMapsLinks,places.location,places.priceLevel,places.rating",
    }

    payload = {
        "includedTypes": [typeOfPlace],
        "maxResultCount": 3,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": 500.0,
            }
        },
    }

    response = requests.post(nearby_search_url, headers=headers, json=payload)

    if response.status_code == 200:
        parsed_data = parse_google_places_tool(response.json()["places"])
        return parsed_data
    else:
        return f"Error {response.status_code}: {response.text}"


def parse_google_places_tool(tool_output) -> str:
    result = ""
    print(type(tool_output))
    for place in tool_output:
        name = place.get("displayName", {}).get("text", "N/A")
        address = place.get("formattedAddress", "N/A")
        rating = place.get("rating", "N/A")
        maps_uri = place.get("googleMapsUri", "N/A")
        price_level = place.get("priceLevel", "N/A")
        price_range = place.get("priceRange", "N/A")

        place_data = f"Name: {name} \nAddress: {address} \nGoogle Maps Rating: {rating} \nGoogle Maps Link: {maps_uri}\n"
        place_data += f"Price Level: {price_level}\n"

        if price_range != "N/A":
            start_price = price_range.get("startPrice", {})
            end_price = price_range.get("endPrice", {})
            place_data += f"Price Range: {start_price['units']} - {end_price['units']} {start_price['currencyCode']}\n"

        result += place_data + "\n"

    return result
