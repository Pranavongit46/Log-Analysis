import pandas as pd
import psycopg2
from psycopg2 import sql

# Load CSV
df = pd.read_csv("auth_logs.csv")

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="cyber_db",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS auth_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    username TEXT NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    login_result TEXT CHECK (login_result IN ('success', 'failure')),
    auth_method TEXT,
    location TEXT
);
""")

# Insert data row by row
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO auth_logs (timestamp, username, ip_address, user_agent, login_result, auth_method, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()
cur.close()
conn.close()

print("ETL completed successfully.")
