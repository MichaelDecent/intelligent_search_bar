import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import DB_CONFIG


def execute_sql(query: str, params: tuple | None = None):
    """Execute a SQL query and return the results."""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall() if cur.description else []
                command = query.strip().split()[0].lower()
                if command in {"insert", "update", "delete", "create", "drop", "alter"}:
                    conn.commit()
        return result
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
