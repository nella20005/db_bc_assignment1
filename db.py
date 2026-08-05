import os
import psycopg2

class LakebaseConnection:
    def __init__(self):
        self.conn = None
    
    def get_connection(self):
        """Get a fresh database connection with OAuth token"""
        if self.conn is None or self.conn.closed:
            cred = self.w.database.generate_database_credential(
                request_id=str(uuid.uuid4()),
                instance_names=[os.environ["PGDATABASE"]]
            )
            
            self.conn = psycopg2.connect(
                host=os.environ["PGHOST"],
                database=os.environ["PGDATABASE"],
                user=os.environ["PGUSER"],
                port=os.environ.get("PGPORT", 5432),
                password=cred.token,
                sslmode="require"
            )
        return self.conn
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and optionally fetch results"""
        conn = self.get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
