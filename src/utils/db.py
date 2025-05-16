import duckdb

def save_inbound_transfers_to_duckdb(inbound_transfers, db_path="log_analysis.duckdb"):
    """Save the parsed log data to a DuckDB database using a MERGE operation."""
    conn = duckdb.connect(db_path)

    # Create a table if it doesn't exist, with filename as the primary key
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inbound_transfers (
            filename TEXT PRIMARY KEY,
            size HUGEINT,
            duration REAL,
            rate REAL,
            action TEXT,
            filetype TEXT,
            start_line_number BIGINT,
            end_line_number BIGINT,
            start_timestamp TIMESTAMP,
            end_timestamp TIMESTAMP
        )
    """)

    # Merge the data into the table
    for transfer in inbound_transfers:
        conn.execute("""
            INSERT INTO inbound_transfers (filename, size, duration, rate, action, filetype, start_line_number, end_line_number, start_timestamp, end_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (filename) DO UPDATE SET
                size = excluded.size,
                duration = excluded.duration,
                rate = excluded.rate,
                action = excluded.action,
                filetype = excluded.filetype,
                start_line_number = excluded.start_line_number,
                end_line_number = excluded.end_line_number,
                start_timestamp = excluded.start_timestamp,
                end_timestamp = excluded.end_timestamp
        """, (
            transfer['filename'], transfer['size'], transfer['duration'], transfer['rate'],
            transfer['action'], transfer['filetype'], transfer['start_line_number'],
            transfer['end_line_number'], transfer['start_timestamp'], transfer['end_timestamp']
        ))

    print(f"Data successfully merged into DuckDB ({db_path}).")
    conn.close()