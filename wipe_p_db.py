import psycopg2

DB_URL = "postgresql://postgres:YXoJPXZYXGznqUZobbxxuedARDJOzwOf@tramway.proxy.rlwy.net:56749/railway"

def wipe_database(db_url):
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    # Get all table names
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public';
    """)
    tables = cur.fetchall()
    for table in tables:
        print(f"Wiping table: {table[0]}")
        cur.execute(f'TRUNCATE TABLE "{table[0]}" RESTART IDENTITY CASCADE;')
    cur.close()
    conn.close()
    print("Database wiped.")

if __name__ == "__main__":
    wipe_database(DB_URL)