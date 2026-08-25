from psycopg2.extras import execute_batch

from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)

BATCH_SIZE = 5_000


def extract_order_items():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Order item extraction started.")

        # ---------------------------------------------------------
        # 1. Extract from source
        # ---------------------------------------------------------

        source_cursor.execute("""
            SELECT
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                discount_amount,
                line_amount,
                created_at,
                updated_at
            FROM tbl_order_items
            ORDER BY order_item_id;
        """)

        order_items = source_cursor.fetchall()

        logger.info(
            "Extracted %s order items from source.",
            len(order_items)
        )

        # ---------------------------------------------------------
        # 2. Clear staging
        # ---------------------------------------------------------

        target_cursor.execute("""
            TRUNCATE TABLE staging.stg_order_items;
        """)

        # ---------------------------------------------------------
        # 3. Load staging
        # ---------------------------------------------------------

        insert_query = """
            INSERT INTO staging.stg_order_items (
                order_item_id,
                order_id,
                product_id,
                quantity,
                unit_price,
                discount_amount,
                line_amount,
                source_created_at,
                source_updated_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            );
        """

        execute_batch(
            target_cursor,
            insert_query,
            order_items,
            page_size=BATCH_SIZE
        )

        target_connection.commit()

        logger.info(
            "Order item staging load completed successfully. "
            "Rows loaded: %s",
            len(order_items)
        )

    except Exception as error:

        target_connection.rollback()

        logger.error(
            "Order item extraction/staging load failed: %s",
            error
        )

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    extract_order_items()