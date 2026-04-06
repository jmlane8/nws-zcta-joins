# 🗺️ GeoJoin Project

This project (and ReadMe.md) was completed with the help of ChatGPT 5.1, Copilot, Gemini and Claude (H3 sections).


## Overview
The **GeoJoin Project** explores different ways to perform **geospatial joins** — operations that combine polygon datasets based on spatial relationships like *intersects* or *contains*.

The goal is to experiment with three complementary technologies **inside Jupyter notebooks**:

| Technology | Description |
|-------------|--------------|
| **PostgreSQL + PostGIS** | The classic spatial database, providing accurate geometry operations and a mature spatial SQL dialect. |
| **Apache Sedona (Spark)** | A distributed geospatial framework for running spatial joins and transformations on large datasets. |
| **DuckDB + Spatial Extension** | A lightweight, single-file analytical database that can read GeoParquet directly and run spatial SQL locally. |
| **H3 (Uber Hexagonal Grid)** | A discrete global grid system that converts polygons into hexagonal cell IDs and joins on shared cells — a fundamentally different, approximate approach. |

These tools will be tested using real public data:
- **ZCTAs (ZIP Code Tabulation Areas)** from the U.S. Census Bureau  
- **National Weather Service (NWS) Forecast Zones and County Warning Areas (CWAs)**

The initial focus is learning and comparison, not benchmarking — the project will visualize and validate how each engine performs spatial joins in practice.

---

## Example question the project will answer
> “Which ZIP Code Tabulation Areas fall within each NWS Forecast Zone or County Warning Area?”

These joins are useful for applications like weather alerting, environmental modeling, and regional data aggregation.

---

## Getting Started

### 1️⃣ Clone the repo
```bash
git clone https://github.com/jmlane8/nws-zcta-joins.git
cd nws-zcta-joins
```

### 2️⃣ Build and start the environment
```bash
docker compose build
docker compose up -d [services you want to load]
```

### 3️⃣ Launch Jupyter
Open your browser to [http://localhost:8888](http://localhost:8888)  
You’ll see notebooks that walk through:
- Running spatial joins in:
  - PostGIS (SQL in PostgreSQL)
  - Sedona (PySpark)
  - DuckDB (SQL or Python API)

---



## Data Sources
| Dataset | Description | URL |
|----------|--------------|-----|
| **ZCTA (ZIP Code Tabulation Areas)** | Census Bureau TIGER/Line polygons | [https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) |
| **NWS Forecast Zones & CWAs** | National Weather Service GIS data | [https://www.weather.gov/gis/PublicZones](https://www.weather.gov/gis/PublicZones) |


wxareas rows:  78
zipcodes rows: 1833
---

## Technology Stack
- **Python 3.12,3.13**
- **JupyterLab**
- **GeoPandas / Shapely / Pyogrio**
- **DuckDB + Spatial Extension**
- **PostgreSQL 16 + PostGIS 3.4**
- **Apache Spark 4.0 + Sedona 1.8**

Each component but DuckDB is containerized in Docker for reproducibility. DuckDB was a data volume.

---

## Future Plans
- Compare runtime and accuracy across engines  
- Integrate with **PMTiles** and **MapLibre** for map visualization  
- Extend to **Phase 2:** extract temperature or weather data from Zarr datasets within polygons  

---

## License
MIT License © 2025 — for research and educational use.

## Indexing 
TL;DR for your benchmark mental model

Postgres/PostGIS: GiST index on geometry → R-tree-like over bounding boxes.

Sedona: R-tree / QuadTree per partition + spatial partitioning (e.g., KDB-tree) for pruning.

DuckDB Spatial: USING RTREE index on geometry.

So conceptually, all three rely on some flavor of bounding-box–based tree (R-tree-ish) as the first-stage spatial pruning, then do exact geometry tests like ST_Intersects or ST_Intersection as refinement.

H3: No R-tree. Instead, each polygon is converted ("polyfilled") into a set of hexagonal cell IDs at a chosen resolution. The spatial join becomes a set intersection of integers — no geometry math at query time. The trade-off is that results are approximate: accuracy improves with higher resolution at the cost of more cells to store and join.

H3 is an approximate join via discretization.

## Discussion
H3 in DuckDB was the fastest (under 100 ms, H3 alone under 300 ms,PostGIS was 400 ms). H3 alone and H3 in DuckDB had fewer successful joins than the R-tree methods (2264 and 2080 vs 2928).
PostGIS was the faster to perform the geojoin the the R-tree like joins (DuckDB and Sedona) DuckDB and PostGIS were easy to set up. Getting the right versions for Spark, Sedona and Java was new for me.