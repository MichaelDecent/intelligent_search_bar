import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import DB_CONFIG


def execute_sql(query: str):
    """Executes a SQL query and returns the results."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
