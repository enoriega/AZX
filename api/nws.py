# HW: write script that takes lat, lon_box; use code we wrote to fetch weather advisories; then prints them out

from dataclasses import dataclass
from datetime import datetime

from typing import Any, List
import requests

@dataclass
class WeatherAlert:
    lat: float
    lon: float
    type: str
    description: str
    starts: datetime
    expires: datetime

def get_alerts(lat:float, lon:float) -> List[WeatherAlert]:
    
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
		
if __name__ == '__main__':
	lat = input('Please enter your latitude: ')
	lon = input('Pleaer your longitude: ')
	print(get_alerts(lat, lon))
