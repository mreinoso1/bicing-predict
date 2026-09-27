def create_grouping_parquet(conn, path: str, destiny):
    conn.sql(f"""
    COPY (
        SELECT id, date_trunc('hour', reported_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Madrid') AS hour_start
        ,dayofweek(reported_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Madrid') AS dow,
        hour(reported_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Madrid') AS hour_report, AVG(available_bikes) as avg_bikes, 
        COUNT(*) AS n_readings
        FROM '{path}'
        WHERE status = 'IN_SERVICE'
        GROUP BY ALL
    ) TO '{destiny}' (FORMAT parquet)
    """)
