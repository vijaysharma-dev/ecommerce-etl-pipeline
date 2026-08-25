from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)


def validate_customer_data():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Customer data quality validation started.")

        # ---------------------------------------------------------
        # 1. Source row count
        # ---------------------------------------------------------

        source_cursor.execute("""
            SELECT COUNT(*)
            FROM tbl_customers;
        """)

        source_count = source_cursor.fetchone()[0]

        logger.info(
            "Source customer count: %s",
            source_count
        )

        # ---------------------------------------------------------
        # 2. Staging row count
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_customers;
        """)

        staging_count = target_cursor.fetchone()[0]

        logger.info(
            "Staging customer count: %s",
            staging_count
        )

        # ---------------------------------------------------------
        # 3. Analytics row count
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.dim_customer;
        """)

        analytics_count = target_cursor.fetchone()[0]

        logger.info(
            "Analytics customer count: %s",
            analytics_count
        )

        # ---------------------------------------------------------
        # 4. NULL customer IDs
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_customers
            WHERE customer_id IS NULL;
        """)

        null_customer_ids = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 5. Duplicate customer IDs
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT customer_id
                FROM staging.stg_customers
                GROUP BY customer_id
                HAVING COUNT(*) > 1
            ) duplicates;
        """)

        duplicate_customer_ids = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # Validation results
        # ---------------------------------------------------------

        if source_count != staging_count:
            raise ValueError(
                f"Source/staging count mismatch: "
                f"{source_count} vs {staging_count}"
            )

        if staging_count != analytics_count:
            raise ValueError(
                f"Staging/analytics count mismatch: "
                f"{staging_count} vs {analytics_count}"
            )

        if null_customer_ids > 0:
            raise ValueError(
                f"Found {null_customer_ids} NULL customer IDs."
            )

        if duplicate_customer_ids > 0:
            raise ValueError(
                f"Found {duplicate_customer_ids} duplicate customer IDs."
            )

        logger.info(
            "Customer data quality validation PASSED."
        )

        logger.info(
            "Validated %s customers successfully.",
            analytics_count
        )

    except Exception as error:

        logger.error(
            "Customer data quality validation FAILED: %s",
            error
        )

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    validate_customer_data()