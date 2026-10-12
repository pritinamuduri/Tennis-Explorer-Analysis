competition = {
    "id": "sr:competition:620",
    "name": "Hopman Cup",
    "type": "mixed",
    "gender": "mixed",
    "category": {
        "id": "sr:category:181",
        "name": "Hopman Cup"
    }
}

print(competition["id"])
print(competition["name"])

competition2 = {
    "id": "sr:competition:660",
    "name": "World Team Cup",
    "type": "mixed",
    "gender": "men"
    # notice: no "parent_id" key at all here
}

print(competition2.get("parent_id"))