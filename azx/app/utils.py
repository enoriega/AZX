from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from geopy import Nominatim


@dataclass
class WeatherAlert:
    lat: float
    lon: float
    type: str
    description: str
    starts: datetime
    expires: datetime


def get_nws_alerts(lat: float, lon: float) -> List[WeatherAlert]:
    endpoint = "https://api.weather.gov/alerts/active"

    params = {
        "point": f"{lat},{lon}"
    }

    response = requests.get(url=endpoint, params=params)

    if response.status_code == 200:
        # We succeeded

        data = response.json()

        ret = list()

        for feature in data['features']:
            props = feature['properties']

            alert = WeatherAlert(
                lat=lat,
                lon=lon,
                type=props['event'],
                description=props['description'],
                starts=props['onset'],
                expires=props['expires']
            )

            ret.append(alert)

        return ret


def resolve_address(address: str):
    """ Gets a location object (with coordinates) using Nomanatim's API """
    geolocator = Nominatim(user_agent="AZX")
    location = geolocator.geocode(address)
    return location

def resolve_coordinates(lat, lon):
    geolocator = Nominatim(user_agent="AZX")
    coordinates = geolocator.reverse(f"{lat},{lon}")
    return coordinates
