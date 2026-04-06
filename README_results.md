wxareas rows:  78
zipcodes rows: 1833

[PostGIS] Intersects join pairs: 2928
  cold: 456.5 ms
  warm: 400.5 ms

[Sedona]
❄️  COLD ST_Intersects: 2928 rows in 6.21s
🔥  WARM ST_Intersects: 2928 rows in 5.27s
✅ Wrote sedona_geojoin_results.csv (via pandas)
Δ warm/cold speed-up: 1.00×


[DuckDB] 
Cold join compute only: 3.446 seconds
Warm join compute only: 2.502 seconds
Successful joins: 2928

[H3 Join]
Cold run (join only): 0.170 seconds
Warm run (join only): 0.226 seconds
Successful joins: 2264


[H3 DuckDB]
Cold join compute only: 0.098 seconds
Warm join compute only: 0.094 seconds
Successful joins: 2080

