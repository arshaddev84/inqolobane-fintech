"""Seed the local PostgreSQL database with synthetic starter data."""

from pathlib import Path

from config.settings import get_settings
from services.seed_data import seed_synthetic_data
from sqlalchemy import create_engine

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = REPOSITORY_ROOT / "data"


def main() -> None:
    """Load fixture CSVs into the configured PostgreSQL database."""
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    with engine.begin() as connection:
        inserted = seed_synthetic_data(connection, DATA_DIRECTORY)
    for table_name, row_count in inserted.items():
        print(f"{table_name}: inserted {row_count} rows")


if __name__ == "__main__":
    main()