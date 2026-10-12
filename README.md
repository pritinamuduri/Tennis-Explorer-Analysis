# 🎾 Tennis Explorer — Sportradar Tennis Data Analytics

A full data pipeline and interactive dashboard built on live Sportradar Tennis API data: competitions, venues/complexes, and ATP/WTA doubles rankings, stored in MySQL and explored through a Streamlit app.

> For a highly detailed, step-by-step build log (including raw data file names, cleaning logic, and troubleshooting notes), see **Tennis_Explorer_Project_Documentation.docx** in this repo.

## Project Overview

This project extracts tennis competition, venue, and doubles-ranking data from the Sportradar Tennis API, transforms the nested JSON into a normalized relational schema, loads it into MySQL, and presents it through an interactive Streamlit dashboard with filters, search, pagination, and charts.

## Tech Stack

- **Python** — data extraction and transformation
- **Sportradar Tennis API** — data source
- **MySQL** — relational database
- **SQLAlchemy + PyMySQL** — database connectivity
- **Streamlit** — interactive web dashboard
- **Plotly** — bar and donut charts
- **pandas** — data handling between SQL and the UI

## Project Structure

```
tennis_explorer/
├── app.py                   # Streamlit dashboard
├── database.py               # DB connection + load_table() upsert function
├── transform.py               # Parses raw API JSON into flat rows
├── load_data.py               # Runs the full extract -> transform -> load pipeline
├── sql_queries.sql            # All 20 required analysis queries
├── requirements.txt            # Python dependencies
├── .env.example                 # Template for required environment variables
├── .env                          # Real secrets (not uploaded — excluded via .gitignore)
├── .gitignore
├── .streamlit/
│   └── config.toml                # App theme
├── sample_response.json            # Cached raw API response: competitions
├── sample_complexes.json           # Cached raw API response: complexes & venues
├── sample_rankings.json            # Cached raw API response: doubles rankings
└── Tennis_Explorer_Project_Documentation.docx   # Full detailed build log
```

## Database Schema

| Table | Description | Key relationships |
|---|---|---|
| `categories` | Tour/category names (ATP, WTA, ITF Men, etc.) | — |
| `competitions` | All tennis competitions | `category_id` → categories, `parent_id` → self (sub-competitions) |
| `complexes` | Sports complexes | — |
| `venues` | Individual courts/venues | `complex_id` → complexes |
| `competitors` | Doubles players | — |
| `competitor_rankings` | Weekly ATP/WTA doubles rankings | `competitor_id` → competitors |

**Note on schema additions:** `competitor_rankings` includes `ranking_name`, `gender`, `year`, and `week` columns beyond the assignment's base spec. These were added because the required analysis (e.g. identifying "the current week", distinguishing ATP from WTA) isn't possible without them — see the docx documentation for full reasoning.

## Setup Instructions

1. **Clone the repository**
   ```
   git clone <your-repo-url>
   cd tennis_explorer
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Create the MySQL database and tables**

   Create the database:
   ```sql
   CREATE DATABASE tennis_db;
   ```
   Then run the six `CREATE TABLE` statements in Section 8 of the docx documentation (or in MySQL Workbench) to set up `categories`, `competitions`, `complexes`, `venues`, `competitors`, and `competitor_rankings`.

4. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your real values:
   ```
   DB_USER=root
   DB_PASSWORD=your_actual_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=tennis_db
   SPORTRADAR_API_KEY=your_actual_sportradar_key
   ```

   Get a free Sportradar trial key at [developer.sportradar.com](https://developer.sportradar.com) — after signing up, make sure to add the **Tennis** API to your application from the Marketplace (a new account has no active subscriptions by default).

5. **Load the data**
   ```
   python load_data.py
   ```
   This fetches competitions, complexes, and doubles rankings from the live API and loads them into MySQL. It's safe to re-run — existing rows are updated in place, not duplicated.

6. **Run the app**
   ```
   streamlit run app.py
   ```

## Features

- **KPI dashboard** — total competitors, countries represented, highest points
- **Top 10 by points** (horizontal bar) and **competitions by gender** (donut chart), both filter-aware
- **Rankings** — sidebar filters for gender, rank range, country, and name search, with a paginated results table
- **Leaderboards** — top-ranked and highest-points tabs
- **Country-wise analysis** — competitor counts and average points per country
- **Competitions search** — filter by category, type, and name
- **Parent/sub-competition explorer** — view tournament hierarchies via a self-join query
- **Venues and complexes** — browse by country
- **Pagination** — all large result sets are paginated at the database level (`LIMIT`/`OFFSET`), so the app never loads an entire table into memory at once

## SQL Queries

All 20 required analysis queries (competitions, venues/complexes, and doubles rankings) are documented with comments in [`sql_queries.sql`](./sql_queries.sql).

## Challenges Faced

- **ISP-level DNS blocking:** `api.sportradar.com` was blocked at the network/DNS level on the development machine's home ISP. Resolved by switching to public DNS (1.1.1.1 / 1.0.0.1) at the OS network level.
- **API trial activation:** A fresh Sportradar account does not automatically grant access to any sport's API — the Tennis API had to be explicitly added via the Marketplace before requests would succeed.
- **MySQL reserved word:** `rank` is reserved in MySQL and had to be wrapped in backticks (`` `rank` ``) everywhere it's referenced.
- **Schema gaps:** The assignment's base schema for `competitor_rankings` has no way to distinguish ATP from WTA or one week from another — extra columns were added to make the required analysis possible.

See the docx documentation for the full troubleshooting log and reasoning behind every design decision.

## Data Source

All data comes from the live [Sportradar Tennis API](https://developer.sportradar.com/tennis/reference/overview) (trial access), covering real ATP, WTA, and ITF competitions, venues, and doubles rankings.
