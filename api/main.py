import uvicorn
from nws import get_alerts

from fastapi import FastAPI
from geocode import geocode

app = FastAPI()

@app.get("/alerts")
def get_weather_alerts(lat:float,lon:float):
    location = get_alerts(lat,lon)
    return location

@app.post("/geocode")
def geocode_integrated(addresses:list[str]):
    ret = list()
    for address in addresses:
        coordinates = geocode(address) # need to modify to match geocode function
        if coordinates == None:
            return None
        else:
            lon = coordinates['x']
            lat = coordinates['y']
            ret.append({"latitude":lat,"longitude":lon})
    return ret

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# return nested list of lat, long dictionaries