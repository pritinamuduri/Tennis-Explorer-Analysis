import requests

response = requests.get("https://api.github.com")
print("Status code:", response.status_code)

data = response.json()
print(type(data))
print(data)