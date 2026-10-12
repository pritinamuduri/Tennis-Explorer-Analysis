import requests
import json

API_KEY = "emgn7WsNuH0yGUJncfAtkSwa6SuWQIXfz3qHj22d"

url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json"
headers = {
    "accept": "application/json",
    "x-api-key": API_KEY
}

response = requests.get(url, headers=headers)
print("Status code:", response.status_code)

data = response.json()
with open("sample_complexes.json", "w") as f:
    json.dump(data, f, indent=2)

print("Total complexes:", len(data["complexes"]))
print(json.dumps(data["complexes"][0], indent=2))


first_complex = data["complexes"][0]
print("Complex id:", first_complex["id"])
print("Complex name:", first_complex["name"])
print("Number of venues in this complex:", len(first_complex["venues"]))
print(json.dumps(first_complex, indent=2))