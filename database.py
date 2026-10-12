import ssl
import streamlit as st
from sqlalchemy import create_engine, text, Table, MetaData
from sqlalchemy.dialects.mysql import insert

DB_USER = "avnadmin"
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = "mysql-2029afe4-gaming-analysis-project.e.aivencloud.com"
DB_PORT = 12498
DB_NAME = "defaultdb"

connection_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

engine = create_engine(connection_url, connect_args={"ssl": ctx})

def load_table(table_name, rows, update_columns):
    """Insert rows into a table. If a row's primary key already exists, update it instead."""
    if not rows:
        print(f"No rows to load into {table_name}")
        return

    # Reflect the table structure from the database
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)

    with engine.begin() as conn:
        for row in rows:
            # Build the MySQL insert statement
            stmt = insert(table).values(row)
            
            # Define which columns to update if a duplicate key occurs
            update_dict = {col: stmt.inserted[col] for col in update_columns}
            stmt = stmt.on_duplicate_key_update(update_dict)
            
            conn.execute(stmt)
            
    print(f"Successfully loaded/updated {len(rows)} rows in {table_name}.")

if __name__ == "__main__":
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connected! Test query result:", result.fetchone())


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
