import requests

API_KEY = "emgn7WsNuH0yGUJncfAtkSwa6SuWQIXfz3qHj22d"   # temporary - we'll fix this properly in a minute
print("Key being used:", repr(API_KEY))
url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json"
headers = {
    "accept": "application/json",
    "x-api-key": API_KEY
}

response = requests.get(url, headers=headers)
import json

data = response.json()

import json
with open("sample_response.json", "w") as f:
    json.dump(data, f, indent=2)

# How many competitions did we get back in total?
print("Total competitions:", len(data["competitions"]))

# Look at just the first one, nicely formatted
first = data["competitions"][0]
print(json.dumps(first, indent=2))