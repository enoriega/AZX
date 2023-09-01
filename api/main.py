import uvicorn
from .nws import get_alerts

from fastapi import FastAPI

app = FastAPI()

@app.get("/alerts")
def get_weather_alerts(lat:float,lon:float):
    location = get_alerts(lat,lon)
    return location

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)