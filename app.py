import os
import uuid
import psycopg2
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Generate database credential
cred = w.database.generate_database_credential(
    request_id=str(uuid.uuid4()),
    instance_names=[os.environ["PGDATABASE"]]
)

# Connect to Lakebase
conn = psycopg2.connect(
    host=os.environ["PGHOST"],
    database=os.environ["PGDATABASE"],
    user=os.environ["PGUSER"],
    port=os.environ.get("PGPORT", 5432),
    password=cred.token,
    sslmode="require"
)

# Use the connection
with conn.cursor() as cur:
    cur.execute("SELECT current_database(), current_user")
    print(cur.fetchone())

conn.close()
