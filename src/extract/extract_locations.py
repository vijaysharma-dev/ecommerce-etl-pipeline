from psycopg2.extras import execute_batch

from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)

BATCH_SIZE = 5_000


def extract_locations():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Location extraction started.")

        source_cursor.execute("""
            SELECT
                location_id,
                city,
                state,
                region,
                pincode,
                created_at,
                updated_at
            FROM tbl_locations
            ORDER BY location_id;
        """)

        locations = source_cursor.fetchall()

        logger.info(
            "Extracted %s locations from source.",
            len(locations)
        )

        target_cursor.execute("""
            TRUNCATE TABLE staging.stg_locations;
        """)

        insert_query = """
            INSERT INTO staging.stg_locations (
                location_id,
                city,
                state,
                region,
                pincode,
                source_created_at,
                source_updated_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s
            );
        """

        execute_batch(
            target_cursor,
            insert_query,
            locations,
            page_size=BATCH_SIZE
        )

        target_connection.commit()

        logger.info(
            "Location staging load completed successfully. "
            "Rows loaded: %s",
            len(locations)
        )

    except Exception as error:

        target_connection.rollback()

        logger.error(
            "Location extraction/staging load failed: %s",
            error
        )

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    extract_locations()