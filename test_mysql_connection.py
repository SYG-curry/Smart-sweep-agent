import sys
import os
import pymysql
from dotenv import load_dotenv

# Windows GBK terminal fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

url = os.getenv("DATABASE_URL", "")
print("DATABASE_URL:", url)
print()

# Parse: mysql+pymysql://user:pass@host:port/dbname?params
try:
    after_scheme = url.split("://")[1]
    auth_host, db_part = after_scheme.split("/", 1)
    user_pass, host_port = auth_host.rsplit("@", 1)
    user, password = user_pass.split(":", 1)
    host, port = host_port.split(":", 1)
    database = db_part.split("?")[0]
except Exception as e:
    print("Failed to parse DATABASE_URL:", e)
    sys.exit(1)

print(f"host={host}  port={port}  user={user}  database={database}")
print()

print("--- Step 1: connect to MySQL server (no db) ---")
try:
    conn = pymysql.connect(host=host, port=int(port), user=user, password=password)
    print("MySQL server connection: OK")
except pymysql.err.OperationalError as e:
    print("MySQL server connection FAILED:", e)
    print()
    print("Possible causes:")
    print("  1. MySQL service is not running")
    print("  2. Wrong username or password")
    print("  3. Wrong host or port")
    sys.exit(1)

print()
print("--- Step 2: check if database exists ---")
cursor = conn.cursor()
cursor.execute("SHOW DATABASES")
databases = [row[0] for row in cursor.fetchall()]

if database in databases:
    print(f"Database '{database}': EXISTS")
    cursor.execute(f"USE `{database}`")
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    if tables:
        print(f"Tables already created: {', '.join(tables)}")
    else:
        print(f"Database '{database}' exists but has NO tables yet.")
        print("-> Start FastAPI service and tables will be created automatically.")
else:
    print(f"Database '{database}': NOT FOUND")
    print(f"Existing databases: {', '.join(databases)}")
    print()
    print("Creating database now...")
    cursor.execute(
        f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    print(f"Database '{database}' created successfully.")
    print("-> Now start FastAPI service and tables will be created automatically.")

cursor.close()
conn.close()
