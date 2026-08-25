from psycopg2.extras import execute_batch

from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)
from src.utils.logger import get_logger


logger = get_logger(__name__)

BATCH_SIZE = 5_000


def extract_products():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        logger.info("Product extraction started.")

        # ---------------------------------------------------------
        # 1. Extract from source
        # ---------------------------------------------------------

        source_cursor.execute("""
            SELECT
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                unit_price,
                cost_price,
                is_active,
                created_at,
                updated_at
            FROM tbl_products
            ORDER BY product_id;
        """)

        products = source_cursor.fetchall()

        logger.info(
            "Extracted %s products from source.",
            len(products)
        )

        # ---------------------------------------------------------
        # 2. Clear staging
        # ---------------------------------------------------------

        target_cursor.execute("""
            TRUNCATE TABLE staging.stg_products;
        """)

        # ---------------------------------------------------------
        # 3. Load staging
        # ---------------------------------------------------------

        insert_query = """
            INSERT INTO staging.stg_products (
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                unit_price,
                cost_price,
                is_active,
                source_created_at,
                source_updated_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            );
        """

        execute_batch(
            target_cursor,
            insert_query,
            products,
            page_size=BATCH_SIZE
        )

        target_connection.commit()

        logger.info(
            "Product staging load completed successfully. "
            "Rows loaded: %s",
            len(products)
        )

    except Exception as error:

        target_connection.rollback()

        logger.error(
            "Product extraction/staging load failed: %s",
            error
        )

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    extract_products()