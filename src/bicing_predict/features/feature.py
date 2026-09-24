def create_grouping_parquet(conn, path: str, destiny: str):
    conn.sql(f"""
    COPY (
        SELECT id, date_trunc('hour',reported_at) as report_hour, AVG(available_bikes)
        FROM '{path}'
        WHERE status == 'IN_SERVICE'
        GROUP BY id, report_hour
    ) TO '{destiny}' (FORMAT parquet)    
    """)
