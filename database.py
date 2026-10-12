from sqlalchemy import create_engine, text

DB_USER = "root"
DB_PASSWORD = "9997275784"   # <-- put your actual MySQL Workbench password
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "tennis_db"

connection_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(connection_url)


if __name__ == "__main__":
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connected! Test query result:", result.fetchone())

def load_table(table_name, rows, update_columns):
    """Insert rows into a table. If a row's primary key already exists, update it instead."""
    if not rows:
        print(f"No rows to load into {table_name}")
        return

    columns = list(rows[0].keys())
    column_list = ", ".join(f"`{col}`" for col in columns)
    placeholders = ", ".join(f":{col}" for col in columns)
    update_clause = ", ".join(f"`{col}` = VALUES(`{col}`)" for col in update_columns)

    sql = text(f"""
        INSERT INTO {table_name} ({column_list})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """)

    with engine.begin() as conn:
        conn.execute(sql, rows)

    print(f"Loaded {len(rows)} rows into {table_name}")