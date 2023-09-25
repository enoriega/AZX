import uvicorn
from nws import get_alerts

from fastapi import FastAPI
from geocode import geocode

app = FastAPI()

@app.get("/alerts")
def get_weather_alerts(lat:float,lon:float):
    location = get_alerts(lat,lon)
    return location

@app.get("/geocode")
def geocode_integrated(address:str):
    coordinates = geocode(address)
    print(coordinates)
    if coordinates == None:
        return None
    else:
        lon = coordinates['x']
        lat = coordinates['y']
        return lat, lon

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)