import streamlit as st
import pandas as pd
from database import engine

st.set_page_config(page_title="Tennis Rankings Explorer", page_icon="🎾", layout="wide")

st.title("🎾 Tennis Rankings Explorer")
st.caption("Explore ATP, WTA and ITF tennis competitions, venues, and doubles rankings — powered by the Sportradar API")


def paginated_table(base_query, params, key, page_size=20):
    count_query = f"SELECT COUNT(*) AS n FROM ({base_query}) AS sub"
    total_rows = pd.read_sql(count_query, engine, params=params)["n"][0]
    total_pages = max(1, -(-total_rows // page_size))

    col_a, col_b = st.columns([1, 4])
    page = col_a.number_input("Page", min_value=1, max_value=total_pages, value=1, key=key)

    offset = (page - 1) * page_size
    paged_query = base_query + " LIMIT %(limit)s OFFSET %(offset)s"
    paged_params = {**params, "limit": page_size, "offset": offset}

    results = pd.read_sql(paged_query, engine, params=paged_params)
    col_b.write(f"Found **{total_rows}** rows · page {page} of {total_pages}")
    st.dataframe(results, use_container_width=True)


# =========================================================
# SIDEBAR: FILTERS  (matches the assignment's sample UI)
# =========================================================
st.sidebar.header("Filters")

years = pd.read_sql("SELECT DISTINCT year FROM competitor_rankings ORDER BY year DESC", engine)
weeks = pd.read_sql("SELECT DISTINCT week FROM competitor_rankings ORDER BY week DESC", engine)
genders = pd.read_sql("SELECT DISTINCT gender FROM competitor_rankings ORDER BY gender", engine)
countries = pd.read_sql("SELECT DISTINCT country FROM competitors ORDER BY country", engine)

selected_year = st.sidebar.selectbox("Year", years["year"].tolist())
selected_week = st.sidebar.selectbox("Week", weeks["week"].tolist())
selected_gender = st.sidebar.selectbox("Gender", ["All"] + genders["gender"].tolist())

min_rank, max_rank = st.sidebar.slider("Rank Range", 1, 500, (1, 100))

selected_country = st.sidebar.selectbox("Country", ["All"] + countries["country"].tolist())
search_name = st.sidebar.text_input("Search Competitors")


# =========================================================
# OVERVIEW METRICS
# =========================================================
with engine.connect() as conn:
    total_competitors = pd.read_sql("SELECT COUNT(*) AS n FROM competitors", conn)["n"][0]
    total_countries = pd.read_sql("SELECT COUNT(DISTINCT country) AS n FROM competitors", conn)["n"][0]
    highest_points = pd.read_sql("SELECT MAX(points) AS n FROM competitor_rankings", conn)["n"][0]

col1, col2, col3 = st.columns(3)
col1.metric("👥 Total Competitors", total_competitors)
col2.metric("🌍 Countries Represented", total_countries)
col3.metric("🏆 Highest Points", highest_points)

st.divider()

# =========================================================
# RANKINGS  (driven entirely by the sidebar filters)
# =========================================================
st.header("Rankings")

query = """
    SELECT c.name, c.country, r.`rank`, r.points, r.movement, r.ranking_name, r.year, r.week
    FROM competitor_rankings r
    JOIN competitors c ON r.competitor_id = c.competitor_id
    WHERE r.year = %(year)s
      AND r.week = %(week)s
      AND r.`rank` BETWEEN %(min_rank)s AND %(max_rank)s
"""
params = {"year": int(selected_year), "week": int(selected_week),
          "min_rank": min_rank, "max_rank": max_rank}

if selected_gender != "All":
    query += " AND r.gender = %(gender)s"
    params["gender"] = selected_gender
if selected_country != "All":
    query += " AND c.country = %(country)s"
    params["country"] = selected_country
if search_name:
    query += " AND c.name LIKE %(name)s"
    params["name"] = f"%{search_name}%"
query += " ORDER BY r.`rank`"

st.subheader("Filtered Rankings")
paginated_table(query, params, key="rank_page")

with st.expander("🏅 Leaderboards"):
    tab1, tab2 = st.tabs(["Top Ranked", "Highest Points"])
    with tab1:
        top_ranked = pd.read_sql("""
            SELECT c.name, c.country, r.`rank`, r.ranking_name
            FROM competitor_rankings r
            JOIN competitors c ON r.competitor_id = c.competitor_id
            ORDER BY r.`rank` LIMIT 10
        """, engine)
        st.dataframe(top_ranked, use_container_width=True)
    with tab2:
        top_points = pd.read_sql("""
            SELECT c.name, c.country, r.points, r.ranking_name
            FROM competitor_rankings r
            JOIN competitors c ON r.competitor_id = c.competitor_id
            ORDER BY r.points DESC LIMIT 10
        """, engine)
        st.dataframe(top_points, use_container_width=True)

with st.expander("🌍 Country-wise analysis"):
    country_stats = pd.read_sql("""
        SELECT c.country, COUNT(*) AS competitor_count, ROUND(AVG(r.points), 1) AS avg_points
        FROM competitor_rankings r
        JOIN competitors c ON r.competitor_id = c.competitor_id
        GROUP BY c.country ORDER BY competitor_count DESC
    """, engine)
    st.dataframe(country_stats, use_container_width=True)
    st.bar_chart(country_stats.set_index("country")["avg_points"].head(15))

st.divider()

# =========================================================
# VENUES AND COMPLEXES  (matches the assignment's sample UI section)
# =========================================================
st.header("Venues and Complexes")

venue_countries = pd.read_sql("SELECT DISTINCT country_name FROM venues ORDER BY country_name", engine)
selected_venue_country = st.selectbox("Filter venues by country", ["All"] + venue_countries["country_name"].tolist())

venue_query = """
    SELECT v.venue_name, v.city_name, cx.complex_name, v.timezone
    FROM venues v
    JOIN complexes cx ON v.complex_id = cx.complex_id
    WHERE 1=1
"""
venue_params = {}
if selected_venue_country != "All":
    venue_query += " AND v.country_name = %(country)s"
    venue_params["country"] = selected_venue_country

paginated_table(venue_query, venue_params, key="venue_page")

with st.expander("📊 Competitions by category"):
    df = pd.read_sql("""
        SELECT cat.category_name, COUNT(*) AS competition_count
        FROM competitions c JOIN categories cat ON c.category_id = cat.category_id
        GROUP BY cat.category_name ORDER BY competition_count DESC
    """, engine)
    st.bar_chart(df.set_index("category_name"))

with st.expander("🔍 Search & filter competitions"):
    categories = pd.read_sql("SELECT category_name FROM categories ORDER BY category_name", engine)
    types = pd.read_sql("SELECT DISTINCT type FROM competitions ORDER BY type", engine)

    c1, c2, c3 = st.columns(3)
    sel_category = c1.selectbox("Category", ["All"] + categories["category_name"].tolist())
    sel_type = c2.selectbox("Type", ["All"] + types["type"].tolist())
    comp_search = c3.text_input("Search competition by name")

    comp_query = """
        SELECT c.competition_name, c.type, c.gender, cat.category_name
        FROM competitions c JOIN categories cat ON c.category_id = cat.category_id
        WHERE 1=1
    """
    comp_params = {}
    if sel_category != "All":
        comp_query += " AND cat.category_name = %(category)s"
        comp_params["category"] = sel_category
    if sel_type != "All":
        comp_query += " AND c.type = %(type)s"
        comp_params["type"] = sel_type
    if comp_search:
        comp_query += " AND c.competition_name LIKE %(name)s"
        comp_params["name"] = f"%{comp_search}%"

    paginated_table(comp_query, comp_params, key="comp_page")

with st.expander("🌳 Parent and sub-competitions"):
    parents = pd.read_sql("""
        SELECT DISTINCT parent.competition_name
        FROM competitions child JOIN competitions parent ON child.parent_id = parent.competition_id
        ORDER BY parent.competition_name
    """, engine)
    selected_parent = st.selectbox("Choose a parent competition", parents["competition_name"])
    subs = pd.read_sql("""
        SELECT child.competition_name, child.type, child.gender
        FROM competitions child JOIN competitions parent ON child.parent_id = parent.competition_id
        WHERE parent.competition_name = %(parent_name)s
    """, engine, params={"parent_name": selected_parent})
    st.dataframe(subs, use_container_width=True)

st.divider()
