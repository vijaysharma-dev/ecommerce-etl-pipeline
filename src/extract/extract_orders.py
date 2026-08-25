from psycopg2.extras import execute_batch

from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)

BATCH_SIZE = 5_000


def extract_orders():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Order extraction started.")

        # ---------------------------------------------------------
        # 1. Extract orders from source database
        # ---------------------------------------------------------

        source_cursor.execute("""
            SELECT
                order_id,
                customer_id,
                location_id,
                order_date,
                order_status,
                payment_status,
                subtotal,
                discount_amount,
                tax_amount,
                shipping_amount,
                total_amount,
                created_at,
                updated_at
            FROM tbl_orders
            ORDER BY order_id;
        """)

        orders = source_cursor.fetchall()

        logger.info(
            "Extracted %s orders from source.",
            len(orders)
        )

        # ---------------------------------------------------------
        # 2. Clear staging table
        # ---------------------------------------------------------

        target_cursor.execute("""
            TRUNCATE TABLE staging.stg_orders;
        """)

        # ---------------------------------------------------------
        # 3. Load orders into staging
        # ---------------------------------------------------------

        insert_query = """
            INSERT INTO staging.stg_orders (
                order_id,
                customer_id,
                location_id,
                order_date,
                order_status,
                payment_status,
                subtotal,
                discount_amount,
                tax_amount,
                shipping_amount,
                total_amount,
                source_created_at,
                source_updated_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            );
        """

        execute_batch(
            target_cursor,
            insert_query,
            orders,
            page_size=BATCH_SIZE
        )

        target_connection.commit()

        logger.info(
            "Order staging load completed successfully. "
            "Rows loaded: %s",
            len(orders)
        )

    except Exception as error:

        target_connection.rollback()

        logger.error(
            "Order extraction/staging load failed: %s",
            error
        )

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    extract_orders()