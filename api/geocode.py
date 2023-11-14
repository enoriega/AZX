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
    result = []
    if len(x['result']['addressMatches']) == 0:
        return None
    else: 
        addressMatches = x['result']['addressMatches']
        for entry in addressMatches:
            coordinates = entry['coordinates'] # instead of looking at first element, create for loop to iterate over addressMatches and store list of sets of coordinates
            result.append(coordinates)
        return result

#if __name__ == '__main__':
#	print(geocode("address test"))