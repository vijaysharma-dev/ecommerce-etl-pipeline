import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_source_connection():
    """Create and return a PostgreSQL connection to the source database."""

    return psycopg2.connect(
        host=os.getenv("SOURCE_DB_HOST"),
        port=os.getenv("SOURCE_DB_PORT"),
        database=os.getenv("SOURCE_DB_NAME"),
        user=os.getenv("SOURCE_DB_USER"),
        password=os.getenv("SOURCE_DB_PASSWORD")
    )


def get_target_connection():
    """Create and return a PostgreSQL connection to the target database."""

    return psycopg2.connect(
        host=os.getenv("TARGET_DB_HOST"),
        port=os.getenv("TARGET_DB_PORT"),
        database=os.getenv("TARGET_DB_NAME"),
        user=os.getenv("TARGET_DB_USER"),
        password=os.getenv("TARGET_DB_PASSWORD")
    )