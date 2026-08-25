from src.utils.db_connection import get_target_connection
from src.utils.logger import get_logger


logger = get_logger(__name__)


def load_locations():
    connection = get_target_connection()
    cursor = connection.cursor()

    try:
        logger.info("Location dimension load started.")

        sql = """
            INSERT INTO analytics.dim_location (
                location_id,
                city,
                state,
                region,
                pincode,
                source_created_at,
                source_updated_at,
                etl_loaded_at
            )
            SELECT
                location_id,
                city,
                state,
                region,
                pincode,
                source_created_at,
                source_updated_at,
                CURRENT_TIMESTAMP
            FROM staging.stg_locations

            ON CONFLICT (location_id)
            DO UPDATE SET
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                region = EXCLUDED.region,
                pincode = EXCLUDED.pincode,
                source_created_at = EXCLUDED.source_created_at,
                source_updated_at = EXCLUDED.source_updated_at,
                etl_loaded_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(sql)

        rows_affected = cursor.rowcount

        connection.commit()

        logger.info(
            "Location dimension load completed successfully. "
            "Rows affected: %s",
            rows_affected
        )

    except Exception as error:

        connection.rollback()

        logger.error(
            "Location dimension load failed: %s",
            error
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_locations()