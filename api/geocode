import requests


def geocode(address:str):
    # url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=4600+Silver+Hill+Rd%2C+Washington%2C+DC+20233&benchmark=2020&format=json"
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
        return coordinates

if __name__ == '__main__':
	print(geocode("2545 E Water St Tucson AZ 87516"))