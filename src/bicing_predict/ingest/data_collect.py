def create_table(conn) -> None:
    conn.sql(""" 
    CREATE TABLE IF NOT EXISTS bicing_6_months (
    id INTEGER NOT NULL,
    reported_at TIMESTAMP NOT NULL,
    status VARCHAR NOT NULL,
    installed INTEGER NOT NULL,
    renting INTEGER NOT NULL,
    is_returning INTEGER NOT NULL,
    available_bikes INTEGER NOT NULL
    )
    """)


def fill_table(conn, path: str) -> None:
    create_table(conn)
    conn.sql(f"""
    INSERT INTO bicing_6_months(id, reported_at, status, installed, renting, is_returning, available_bikes)
    SELECT station_id, to_timestamp(last_reported) AT TIME ZONE 'UTC', status, is_installed, is_renting, is_returning, num_bikes_available
    FROM read_csv('{path}', union_by_name = true, nullstr =['NA'])
    WHERE station_id IS NOT NULL
    AND last_reported IS NOT NULL
    AND status IS NOT NULL
    AND is_installed IS NOT NULL
    AND is_renting IS NOT NULL
    AND is_returning IS NOT NULL
    AND num_bikes_available IS NOT NULL
    AND to_timestamp(last_reported) AT TIME ZONE 'UTC' >= TIMESTAMP '2026-02-01'
    AND to_timestamp(last_reported) AT TIME ZONE 'UTC' < TIMESTAMP '2026-09-01'
    """)


def create_parquet(conn) -> None:
    conn.sql(""" 
    COPY (SELECT * FROM bicing_6_months) TO 'bicing.parquet' (FORMAT parquet)   
    """)
