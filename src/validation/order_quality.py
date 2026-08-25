from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)


def validate_order_data():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Order data quality validation started.")

        # ---------------------------------------------------------
        # 1. Source count
        # ---------------------------------------------------------

        source_cursor.execute("""
            SELECT COUNT(*)
            FROM tbl_orders;
        """)

        source_count = source_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 2. Staging count
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM staging.stg_orders;
        """)

        staging_count = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 3. Fact count
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.fact_order;
        """)

        fact_count = target_cursor.fetchone()[0]

        logger.info("Source order count: %s", source_count)
        logger.info("Staging order count: %s", staging_count)
        logger.info("Fact order count: %s", fact_count)

        # ---------------------------------------------------------
        # 4. Duplicate order IDs in staging
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT order_id
                FROM staging.stg_orders
                GROUP BY order_id
                HAVING COUNT(*) > 1
            ) duplicates;
        """)

        duplicate_orders = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 5. NULL customer keys
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.fact_order
            WHERE customer_key IS NULL;
        """)

        null_customer_keys = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 6. Orphan customer keys
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.fact_order f
            LEFT JOIN analytics.dim_customer c
                ON f.customer_key = c.customer_key
            WHERE c.customer_key IS NULL;
        """)

        orphan_customer_keys = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # 7. Invalid financial values
        # ---------------------------------------------------------

        target_cursor.execute("""
            SELECT COUNT(*)
            FROM analytics.fact_order
            WHERE subtotal < 0
               OR discount_amount < 0
               OR tax_amount < 0
               OR shipping_amount < 0
               OR total_amount < 0;
        """)

        invalid_financial_rows = target_cursor.fetchone()[0]

        # ---------------------------------------------------------
        # Validation rules
        # ---------------------------------------------------------

        if source_count != staging_count:
            raise ValueError(
                f"Source/staging count mismatch: "
                f"{source_count} vs {staging_count}"
            )

        if staging_count != fact_count:
            raise ValueError(
                f"Staging/fact count mismatch: "
                f"{staging_count} vs {fact_count}"
            )

        if duplicate_orders > 0:
            raise ValueError(
                f"Found {duplicate_orders} duplicate order IDs."
            )

        if null_customer_keys > 0:
            raise ValueError(
                f"Found {null_customer_keys} NULL customer keys."
            )

        if orphan_customer_keys > 0:
            raise ValueError(
                f"Found {orphan_customer_keys} orphan customer keys."
            )

        if invalid_financial_rows > 0:
            raise ValueError(
                f"Found {invalid_financial_rows} orders "
                "with invalid financial values."
            )

        logger.info("Order data quality validation PASSED.")

        logger.info(
            "Validated %s orders successfully.",
            fact_count
        )

    except Exception as error:

        logger.error(
            "Order data quality validation FAILED: %s",
            error
        )

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    validate_order_data()