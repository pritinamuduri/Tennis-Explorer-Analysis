import requests
import json

API_KEY = "emgn7WsNuH0yGUJncfAtkSwa6SuWQIXfz3qHj22d"

url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json"
headers = {
    "accept": "application/json",
    "x-api-key": API_KEY
}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)

data = response.json()
with open("sample_rankings.json", "w") as f:
    json.dump(data, f, indent=2)

print("Number of ranking lists (tours):", len(data["rankings"]))
first_tour = data["rankings"][0]
print("Tour name:", first_tour["name"], "| gender:", first_tour["gender"], "| year:", first_tour.get("year"), "| week:", first_tour.get("week"))
print("Competitors in this tour's list:", len(first_tour["competitor_rankings"]))
print(json.dumps(first_tour["competitor_rankings"][0], indent=2))