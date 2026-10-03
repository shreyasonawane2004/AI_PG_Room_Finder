import os
import pymysql
from pymysql.cursors import DictCursor
from flask import current_app, g

def get_connection_params(use_database=True):
    """Retrieve database connection parameters from Flask config or environment."""
    if current_app:
        config = current_app.config
        host = config.get("DB_HOST", "localhost")
        port = config.get("DB_PORT", 3306)
        user = config.get("DB_USER", "root")
        password = config.get("DB_PASSWORD", "")
        db_name = config.get("DB_NAME", "ai_pg_room_finder") if use_database else None
    else:
        from app.config import Config
        host = Config.DB_HOST
        port = Config.DB_PORT
        user = Config.DB_USER
        password = Config.DB_PASSWORD
        db_name = Config.DB_NAME if use_database else None

    params = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False
    }
    if db_name:
        params["database"] = db_name
    return params


def get_db():
    """Get or create a request-bound MySQL database connection."""
    if "db" not in g:
        params = get_connection_params(use_database=True)
        try:
            g.db = pymysql.connect(**params)
        except pymysql.MySQLError as err:
            raise ConnectionError(
                f"Failed to connect to MySQL database '{params.get('database')}': {err}. "
                "Please verify your credentials in the .env file."
            ) from err
    return g.db


def close_db(e=None):
    """Close the request-bound database connection."""
    db = g.pop("db", None)
    if db is not None and db.open:
        db.close()


def query_db(query, args=(), one=False, commit=False):
    """
    Execute a parameterized SQL query safely.
    - query: SQL statement with %s placeholders
    - args: tuple/list of parameters
    - one: return single record if True, else list of records
    - commit: commit transaction and return lastrowid
    """
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            return cursor.lastrowid
        result = cursor.fetchall()
        return (result[0] if result else None) if one else result


def execute_many(query, args_list, commit=True):
    """Execute a parameterized query over a list of parameter sets."""
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.executemany(query, args_list)
        if commit:
            conn.commit()
        return cursor.rowcount


def check_db_connection():
    """Test MySQL connectivity and return (status_bool, message)."""
    try:
        params = get_connection_params(use_database=False)
        conn = pymysql.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version;")
            row = cursor.fetchone()
            version = row["version"] if row else "Unknown"
        conn.close()
        return True, f"Connected to MySQL server (Version {version})"
    except pymysql.MySQLError as err:
        return False, str(err)


def execute_sql_file(file_path, conn):
    """Execute multi-statement SQL script file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split statements by semicolon while ignoring comments
    statements = []
    current_stmt = []
    for line in content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("--") or not trimmed:
            continue
        current_stmt.append(line)
        if trimmed.endswith(";"):
            statement = "\n".join(current_stmt).strip()
            if statement:
                statements.append(statement)
            current_stmt = []

    with conn.cursor() as cursor:
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except pymysql.MySQLError as e:
                # Log warning but continue for robust seeding
                pass
    conn.commit()


def init_db(seed=True):
    """
    Initialize database schema and seed data using settings from environment variables.
    """
    params = get_connection_params(use_database=False)
    db_name = os.getenv("DB_NAME", "ai_pg_room_finder")

    conn = pymysql.connect(**params)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{db_name}`;")
        conn.commit()

        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        schema_path = os.path.join(base_dir, "database", "schema.sql")
        seed_path = os.path.join(base_dir, "database", "seed_data.sql")

        if os.path.exists(schema_path):
            execute_sql_file(schema_path, conn)

        if seed and os.path.exists(seed_path):
            execute_sql_file(seed_path, conn)

        return True, f"Database '{db_name}' initialized and seeded successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
