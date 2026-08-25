from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)


def validate_location_data():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Location data quality validation started.")

        # Source count
        source_cursor.execute("""
            SELECT COUNT(*)
            FROM tbl_locations;
        """)

        source_count = source_cursor.fetchone()[0]

        # Staging count
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_locations;
        """)

        staging_count = target_cursor.fetchone()[0]

        # Dimension count
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.dim_location;
        """)

        dimension_count = target_cursor.fetchone()[0]

        logger.info("Source location count: %s", source_count)
        logger.info("Staging location count: %s", staging_count)
        logger.info("Dimension location count: %s", dimension_count)

        # NULL IDs
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_locations
            WHERE location_id IS NULL;
        """)

        null_location_ids = target_cursor.fetchone()[0]

        # Duplicate IDs
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT location_id
                FROM staging.stg_locations
                GROUP BY location_id
                HAVING COUNT(*) > 1
            ) duplicates;
        """)

        duplicate_location_ids = target_cursor.fetchone()[0]

        # Validation
        if source_count != staging_count:
            raise ValueError(
                f"Source/staging count mismatch: "
                f"{source_count} vs {staging_count}"
            )

        if staging_count != dimension_count:
            raise ValueError(
                f"Staging/dimension count mismatch: "
                f"{staging_count} vs {dimension_count}"
            )

        if null_location_ids > 0:
            raise ValueError(
                f"Found {null_location_ids} NULL location IDs."
            )

        if duplicate_location_ids > 0:
            raise ValueError(
                f"Found {duplicate_location_ids} duplicate location IDs."
            )

        logger.info(
            "Location data quality validation PASSED."
        )

        logger.info(
            "Validated %s locations successfully.",
            dimension_count
        )

    except Exception as error:

        logger.error(
            "Location data quality validation FAILED: %s",
            error
        )

        raise

    finally:
        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    validate_location_data()