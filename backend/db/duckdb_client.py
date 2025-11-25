"""
DuckDB Client
Manages connection to the analytical database
"""
import duckdb
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Global connection
_conn = None

def init_db():
    """Initialize DuckDB connection"""
    global _conn
    
    # Path to DuckDB file
    db_path = Path(__file__).parent.parent.parent / "data" / "canonical" / "canonical.duckdb"
    
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB file not found: {db_path}")
    
    _conn = duckdb.connect(str(db_path), read_only=True)
    logger.info(f"Connected to DuckDB: {db_path}")
    
    return _conn

def get_db():
    """Get the current database connection"""
    global _conn
    if _conn is None:
        init_db()
    return _conn

def close_db():
    """Close the database connection"""
    global _conn
    if _conn:
        _conn.close()
        _conn = None
        logger.info("DuckDB connection closed")

def query_to_dict(query: str):
    """Execute query and return results as list of dicts.

    This wrapper adds basic error handling and ensures callers always
    receive a list (possibly empty) rather than an exception bubbling up
    for common DB issues. This makes downstream code more robust and
    easier to test.
    """
    try:
        conn = get_db()
        result = conn.execute(query).fetchdf()
        if result is None or len(result) == 0:
            logger.debug("query_to_dict: query returned no rows")
            return []
        return result.to_dict('records')
    except Exception as e:
        logger.warning(f"query_to_dict failed: {e}")
        return []

def query_to_df(query: str):
    """Execute query and return results as pandas DataFrame"""
    conn = get_db()
    return conn.execute(query).fetchdf()
