import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "conservacion_marina")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True, future=True)


def run_query(sql: str, params: dict | None = None) -> list[dict]:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]