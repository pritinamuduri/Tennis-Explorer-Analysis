CREATE DATABASE IF NOT EXISTS tennis_db;
USE tennis_db;

CREATE TABLE categories (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);


CREATE TABLE competitions (
    competition_id VARCHAR(50) PRIMARY KEY,
    competition_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(50),
    type VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    category_id VARCHAR(50),
    level VARCHAR(30),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);


CREATE TABLE complexes (
    complex_id VARCHAR(50) PRIMARY KEY,
    complex_name VARCHAR(100) NOT NULL
);


CREATE TABLE venues (
    venue_id VARCHAR(50) PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    city_name VARCHAR(100),
    country_name VARCHAR(100),
    country_code CHAR(3),
    timezone VARCHAR(100),
    complex_id VARCHAR(50),
    FOREIGN KEY (complex_id) REFERENCES complexes(complex_id)
);


CREATE TABLE competitors (
    competitor_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    country_code CHAR(3),
    abbreviation VARCHAR(10)
);

CREATE TABLE competitor_rankings (
    rank_id INT AUTO_INCREMENT PRIMARY KEY,
    `rank` INT NOT NULL,
    movement INT,
    points INT,
    competitions_played INT,
    ranking_name VARCHAR(10),
    gender VARCHAR(10),
    year SMALLINT,
    week SMALLINT,
    competitor_id VARCHAR(50),
    FOREIGN KEY (competitor_id) REFERENCES competitors(competitor_id)
);

SELECT c.competition_name, cat.category_name
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
LIMIT 10;


######-----------------------------------------------######
#Query 1 — List all competitions along with their category name
SELECT c.competition_name, c.type, c.gender, cat.category_name
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id;

#Query 2 — Count the number of competitions in each category
SELECT cat.category_name, COUNT(*) AS competition_count
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY competition_count DESC;

#Query 3 — Find all competitions of type 'doubles'
SELECT competition_name, gender, category_id
FROM competitions
WHERE type = 'doubles';

#Query 4 — Get competitions that belong to a specific category 
SELECT c.competition_name, c.type, c.gender
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
WHERE cat.category_name = 'ITF Men';

-- Query 5 — Identify parent competitions and their sub-competitions
SELECT child.competition_name AS sub_competition,
       parent.competition_name AS parent_competition
FROM competitions child
JOIN competitions parent ON child.parent_id = parent.competition_id
LIMIT 20;


-- Query 6 — Analyze the distribution of competition types by category
SELECT cat.category_name, c.type, COUNT(*) AS competition_count
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
GROUP BY cat.category_name, c.type
ORDER BY cat.category_name, competition_count DESC;


-- Query 7 — List all competitions with no parent (top-level competitions)
SELECT competition_name, type, gender, level
FROM competitions
WHERE parent_id IS NULL;

-- ===================== VENUES AND COMPLEXES =====================

-- Query 1 — List all venues along with their associated complex name
SELECT v.venue_name, v.city_name, v.country_name, cx.complex_name
FROM venues v
JOIN complexes cx ON v.complex_id = cx.complex_id;


-- Query 2 — Count the number of venues in each complex
SELECT cx.complex_name, COUNT(*) AS venue_count
FROM venues v
JOIN complexes cx ON v.complex_id = cx.complex_id
GROUP BY cx.complex_name
ORDER BY venue_count DESC;


-- Query 3 — Get details of venues in a specific country (e.g. Chile)
SELECT venue_name, city_name, country_name, timezone
FROM venues
WHERE country_name = 'Chile';


-- Query 4 — Identify all venues and their timezones
SELECT venue_name, city_name, timezone
FROM venues;


-- Query 5 — Find complexes that have more than one venue
SELECT cx.complex_name, COUNT(*) AS venue_count
FROM venues v
JOIN complexes cx ON v.complex_id = cx.complex_id
GROUP BY cx.complex_name
HAVING COUNT(*) > 1
ORDER BY venue_count DESC;


-- Query 6 — List venues grouped by country
SELECT country_name, COUNT(*) AS venue_count
FROM venues
GROUP BY country_name
ORDER BY venue_count DESC;


-- Query 7 — Find all venues for a specific complex (e.g. Nacional)
SELECT v.venue_name, v.city_name, v.country_name
FROM venues v
JOIN complexes cx ON v.complex_id = cx.complex_id
WHERE cx.complex_name = 'Nacional';


-- ===================== DOUBLES COMPETITOR RANKINGS =====================

-- Query 1 — Get all competitors with their rank and points
SELECT c.name, r.`rank`, r.points, r.ranking_name
FROM competitor_rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id;


-- Query 2 — Find competitors ranked in the top 5
SELECT c.name, r.`rank`, r.points, r.ranking_name
FROM competitor_rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.`rank` <= 5
ORDER BY r.ranking_name, r.`rank`;


-- Query 3 — List competitors with no rank movement (stable rank)
SELECT c.name, r.`rank`, r.movement, r.ranking_name
FROM competitor_rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.movement = 0;


-- Query 4 — Get the total points of competitors from a specific country (e.g. Croatia)
SELECT c.country, SUM(r.points) AS total_points
FROM competitor_rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE c.country = 'Croatia'
GROUP BY c.country;


-- Query 5 — Count the number of competitors per country
SELECT country, COUNT(*) AS competitor_count
FROM competitors
GROUP BY country
ORDER BY competitor_count DESC;


-- Query 6 — Find competitors with the highest points in the current week
SELECT c.name, r.points, r.ranking_name, r.year, r.week
FROM competitor_rankings r
JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.year = (SELECT MAX(year) FROM competitor_rankings)
  AND r.week = (SELECT MAX(week) FROM competitor_rankings WHERE year = (SELECT MAX(year) FROM competitor_rankings))
ORDER BY r.points DESC
LIMIT 10;