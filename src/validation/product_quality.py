from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)


def validate_product_data():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Product data quality validation started.")

        # Source count
        source_cursor.execute("""
            SELECT COUNT(*)
            FROM tbl_products;
        """)

        source_count = source_cursor.fetchone()[0]

        # Staging count
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_products;
        """)

        staging_count = target_cursor.fetchone()[0]

        # Analytics count
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.dim_product;
        """)

        analytics_count = target_cursor.fetchone()[0]

        logger.info("Source product count: %s", source_count)
        logger.info("Staging product count: %s", staging_count)
        logger.info("Analytics product count: %s", analytics_count)

        # NULL product IDs
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_products
            WHERE product_id IS NULL;
        """)

        null_product_ids = target_cursor.fetchone()[0]

        # Duplicate product IDs
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT product_id
                FROM staging.stg_products
                GROUP BY product_id
                HAVING COUNT(*) > 1
            ) duplicates;
        """)

        duplicate_product_ids = target_cursor.fetchone()[0]

        # Invalid prices
        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_products
            WHERE unit_price <= 0
               OR cost_price < 0;
        """)

        invalid_prices = target_cursor.fetchone()[0]

        # Validations
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

        if null_product_ids > 0:
            raise ValueError(
                f"Found {null_product_ids} NULL product IDs."
            )

        if duplicate_product_ids > 0:
            raise ValueError(
                f"Found {duplicate_product_ids} duplicate product IDs."
            )

        if invalid_prices > 0:
            raise ValueError(
                f"Found {invalid_prices} products with invalid prices."
            )

        logger.info("Product data quality validation PASSED.")

        logger.info(
            "Validated %s products successfully.",
            analytics_count
        )

    except Exception as error:

        logger.error(
            "Product data quality validation FAILED: %s",
            error
        )

        raise

    finally:
        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    validate_product_data()