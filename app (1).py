import streamlit as st
import pandas as pd
import plotly.express as px
from database import engine

st.set_page_config(page_title="Tennis Rankings Explorer", page_icon="🎾", layout="wide")

st.title("🎾 Tennis Rankings Explorer")
st.caption("Explore ATP, WTA and ITF tennis competitions, venues, and doubles rankings — powered by the Sportradar API")

GREEN_SCALE = "Greens"
GENDER_COLORS = {"men": "#1f77b4", "women": "#e377c2", "mixed": "#2E7D32"}


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


def horizontal_bar(df, x_col, y_col, title=None):
    fig = px.bar(
        df.sort_values(x_col), x=x_col, y=y_col,
        orientation="h", color=x_col, color_continuous_scale=GREEN_SCALE,
        text=x_col, title=title
    )
    fig.update_layout(xaxis_title=x_col.replace("_", " ").title(), yaxis_title="",
                       coloraxis_showscale=False, showlegend=False)
    fig.update_xaxes(tickangle=0)
    st.plotly_chart(fig, use_container_width=True)


def vertical_bar(df, x_col, y_col, title=None):
    fig = px.bar(
        df, x=x_col, y=y_col,
        color=y_col, color_continuous_scale=GREEN_SCALE, title=title
    )
    fig.update_layout(xaxis_title="", yaxis_title=y_col.replace("_", " ").title(),
                       coloraxis_showscale=False)
    fig.update_xaxes(tickangle=0)
    st.plotly_chart(fig, use_container_width=True)


def donut_chart(df, names_col, values_col, color_map=None, title=None):
    fig = px.pie(
        df, names=names_col, values=values_col, hole=0.5,
        color=names_col, color_discrete_map=color_map, title=title
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# SIDEBAR: FILTERS
# =========================================================
st.sidebar.header("Filters")

ranking_genders = pd.read_sql("SELECT DISTINCT gender FROM competitor_rankings", engine)["gender"].tolist()
competition_genders = pd.read_sql("SELECT DISTINCT gender FROM competitions", engine)["gender"].tolist()
all_genders = sorted(set(ranking_genders) | set(competition_genders))

countries = pd.read_sql("SELECT DISTINCT country FROM competitors ORDER BY country", engine)

selected_gender = st.sidebar.selectbox("Gender", ["All"] + all_genders)
min_rank, max_rank = st.sidebar.slider("Rank Range", 1, 500, (1, 100))
selected_country = st.sidebar.selectbox("Country", ["All"] + countries["country"].tolist())
search_name = st.sidebar.text_input("Search Competitors")

latest_period = pd.read_sql("""
    SELECT year, week FROM competitor_rankings
    ORDER BY year DESC, week DESC LIMIT 1
""", engine).iloc[0]
latest_year, latest_week = int(latest_period["year"]), int(latest_period["week"])


# =========================================================
# OVERVIEW METRICS (KPIs)
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
# SHARED FILTER QUERY (used by charts below AND the table further down)
# =========================================================
rankings_query = """
    SELECT c.name, c.country, r.`rank`, r.points, r.movement, r.ranking_name
    FROM competitor_rankings r
    JOIN competitors c ON r.competitor_id = c.competitor_id
    WHERE r.year = %(year)s
      AND r.week = %(week)s
      AND r.`rank` BETWEEN %(min_rank)s AND %(max_rank)s
"""
rankings_params = {"year": latest_year, "week": latest_week,
                    "min_rank": min_rank, "max_rank": max_rank}

if selected_gender != "All":
    rankings_query += " AND r.gender = %(gender)s"
    rankings_params["gender"] = selected_gender
if selected_country != "All":
    rankings_query += " AND c.country = %(country)s"
    rankings_params["country"] = selected_country
if search_name:
    rankings_query += " AND c.name LIKE %(name)s"
    rankings_params["name"] = f"%{search_name}%"

# ---- Two charts, side by side, right below the KPIs ----
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🏆 Top 10 by points")
    top10_query = rankings_query.replace(
        "SELECT c.name, c.country, r.`rank`, r.points, r.movement, r.ranking_name",
        "SELECT c.name, r.points"
    ) + " ORDER BY r.points DESC LIMIT 10"
    top10 = pd.read_sql(top10_query, engine, params=rankings_params)
    if top10.empty:
        st.info("No competitors match the current filters.")
    else:
        horizontal_bar(top10, "points", "name")

with chart_col2:
    st.subheader("🥧 Competitions by gender")
    gender_query = "SELECT gender, COUNT(*) AS competition_count FROM competitions"
    gender_params = {}
    if selected_gender != "All":
        gender_query += " WHERE gender = %(gender)s"
        gender_params["gender"] = selected_gender
    gender_query += " GROUP BY gender"
    gender_dist = pd.read_sql(gender_query, engine, params=gender_params)
    if gender_dist.empty:
        st.info("No competitions match the current gender filter.")
    else:
        donut_chart(gender_dist, "gender", "competition_count", color_map=GENDER_COLORS)

st.divider()

# =========================================================
# RANKINGS TABLE
# =========================================================
st.header("Rankings")
paginated_table(rankings_query + " ORDER BY r.`rank`", rankings_params, key="rank_page")

with st.expander("🏅 Leaderboards"):
    tab1, tab2 = st.tabs(["Top Ranked", "Highest Points"])
    with tab1:
        top_ranked = pd.read_sql(rankings_query + " ORDER BY r.`rank` LIMIT 10",
                                  engine, params=rankings_params)
        st.dataframe(top_ranked[["name", "country", "rank", "ranking_name"]], use_container_width=True)
    with tab2:
        top_points = pd.read_sql(rankings_query + " ORDER BY r.points DESC LIMIT 10",
                                  engine, params=rankings_params)
        st.dataframe(top_points[["name", "country", "points", "ranking_name"]], use_container_width=True)

with st.expander("🌍 Country-wise analysis"):
    country_stats = pd.read_sql("""
        SELECT c.country, COUNT(*) AS competitor_count, ROUND(AVG(r.points), 1) AS avg_points
        FROM competitor_rankings r
        JOIN competitors c ON r.competitor_id = c.competitor_id
        WHERE r.year = %(year)s AND r.week = %(week)s
        GROUP BY c.country ORDER BY competitor_count DESC
    """, engine, params={"year": latest_year, "week": latest_week})
    st.dataframe(country_stats, use_container_width=True)
    vertical_bar(country_stats.head(15), "country", "avg_points")

st.divider()

# =========================================================
# VENUES AND COMPLEXES
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
    vertical_bar(df, "category_name", "competition_count")

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
st.caption("Built with Python, MySQL, and Streamlit · Data from the Sportradar Tennis API")