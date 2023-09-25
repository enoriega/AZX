import uvicorn
import requests
from nws import get_alerts

from fastapi import FastAPI

def geocode(address:str):
    endpoint = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

    params = {
        "address": address,
        "benchmark": "2020",
        "format": "json"
    }

    response = requests.get(url=endpoint, params=params)
    x = response.json()
    if len(x['result']['addressMatches']) == 0:
          return None
    else: 
        coordinates = x['result']['addressMatches'][0]['coordinates']
        lon = coordinates[0]
        lat = coordinates[1]

app = FastAPI()

@app.get("/alerts")
def get_weather_alerts(lat:float,lon:float):
    location = get_alerts(lat,lon)
    return location

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)