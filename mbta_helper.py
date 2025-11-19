import os
import json
import urllib.request
from urllib.parse import urlencode
from dotenv import load_dotenv


# Load API keys from .env
load_dotenv()

MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

MAPBOX_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/forward"
MBTA_STOP_URL = "https://api-v3.mbta.com/stops"



# Helper: GET JSON from a URL
def get_json(url: str) -> dict:
    """Retrieve JSON data from a URL and return as a Python dict."""
    with urllib.request.urlopen(url) as response:
        data = response.read().decode("utf-8")
        return json.loads(data)


# Step 1: Geocode using Mapbox
def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name, return (latitude, longitude) as strings.
    Uses Mapbox forward geocoding.
    """
    if not MAPBOX_API_KEY:
        raise RuntimeError("MAPBOX_TOKEN is missing. Check your .env file.")

    # Build the URL properly
    params = {
        "q": place_name,
        "access_token": MAPBOX_API_KEY
    }

    url = MAPBOX_BASE_URL + "?" + urlencode(params)

    data = get_json(url)

    try:
        feature = data["features"][0]
        coords = feature["geometry"]["coordinates"]  # [lon, lat]
        lon, lat = coords[0], coords[1]
        return str(lat), str(lon)

    except (KeyError, IndexError):
        raise ValueError(f"Could not find coordinates for '{place_name}'")


# Step 2: MBTA API — Get nearest station
def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude, return tuple:
    (stop_name, wheelchair_accessible)
    """
    if not MBTA_API_KEY:
        raise RuntimeError("MBTA_API_KEY is missing. Check your .env file.")

    params = {
        "api_key": MBTA_API_KEY,
        "sort": "distance",
        "filter[latitude]": latitude,
        "filter[longitude]": longitude,
    }

    url = MBTA_STOP_URL + "?" + urlencode(params)

    data = get_json(url)

    try:
        stop = data["data"][0]

        stop_name = stop["attributes"]["name"]
        wheelchair = stop["attributes"]["wheelchair_boarding"]

        # MBTA API: 1 = accessible, 2 = not accessible, 0 = unknown
        is_accessible = (wheelchair == 1)

        return stop_name, is_accessible

    except (KeyError, IndexError):
        raise ValueError("No MBTA stops found near that location.")


# Step 3: Combined tool
def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Take a place name, return (nearest_stop_name, accessibility_bool)
    """
    lat, lon = get_lat_lng(place_name)
    return get_nearest_station(lat, lon)


# Testing in main()
def main():
    # Test 1 — Boston Common
    print("Testing get_lat_lng('Boston Common'):")
    print(get_lat_lng("Boston Common"))

    print("\nTesting find_stop_near('Boston Common'):")
    print(find_stop_near("Boston Common"))

    # Test 2 — Fenway Park
    print("\nTesting get_lat_lng('Fenway Park'):")
    print(get_lat_lng("Fenway Park"))

    print("\nTesting find_stop_near('Fenway Park'):")
    print(find_stop_near("Fenway Park"))


if __name__ == "__main__":
    main()

