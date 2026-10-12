import json
from transform import parse_competitions, parse_complexes, parse_doubles_rankings
from database import load_table

# ---- Competitions ----
with open("sample_response.json") as f:
    payload = json.load(f)

categories, competitions = parse_competitions(payload)
load_table("categories", categories, update_columns=["category_name"])
load_table("competitions", competitions, update_columns=[
    "competition_name", "parent_id", "type", "gender", "category_id", "level"
])

# ---- Complexes and venues ----
with open("sample_complexes.json") as f:
    complexes_payload = json.load(f)

complexes, venues = parse_complexes(complexes_payload)
load_table("complexes", complexes, update_columns=["complex_name"])
load_table("venues", venues, update_columns=[
    "venue_name", "city_name", "country_name", "country_code", "timezone", "complex_id"
])

# ---- Competitors and rankings ----
with open("sample_rankings.json") as f:
    rankings_payload = json.load(f)

competitors, rankings = parse_doubles_rankings(rankings_payload)
load_table("competitors", competitors, update_columns=[
    "name", "country", "country_code", "abbreviation"
])
load_table("competitor_rankings", rankings, update_columns=[
    "rank", "movement", "points", "competitions_played", "ranking_name", "gender", "year", "week"
])