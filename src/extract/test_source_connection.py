import os

import psycopg2
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


def test_source_connection():
    connection = psycopg2.connect(
        host=os.getenv("SOURCE_DB_HOST"),
        port=os.getenv("SOURCE_DB_PORT"),
        database=os.getenv("SOURCE_DB_NAME"),
        user=os.getenv("SOURCE_DB_USER"),
        password=os.getenv("SOURCE_DB_PASSWORD")
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT current_database(), current_user;
    """)

    result = cursor.fetchone()

    print("Database:", result[0])
    print("User:", result[1])

    cursor.close()
    connection.close()


if __name__ == "__main__":
    test_source_connection()