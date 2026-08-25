from src.utils.db_connection import get_target_connection
from src.utils.logger import get_logger


logger = get_logger(__name__)


def load_products():
    connection = get_target_connection()
    cursor = connection.cursor()

    try:
        logger.info("Product dimension load started.")

        sql = """
            INSERT INTO analytics.dim_product (
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                unit_price,
                cost_price,
                is_active,
                source_created_at,
                source_updated_at,
                etl_loaded_at
            )
            SELECT
                product_id,
                product_name,
                category,
                subcategory,
                brand,
                unit_price,
                cost_price,
                is_active,
                source_created_at,
                source_updated_at,
                CURRENT_TIMESTAMP
            FROM staging.stg_products

            ON CONFLICT (product_id)
            DO UPDATE SET
                product_name = EXCLUDED.product_name,
                category = EXCLUDED.category,
                subcategory = EXCLUDED.subcategory,
                brand = EXCLUDED.brand,
                unit_price = EXCLUDED.unit_price,
                cost_price = EXCLUDED.cost_price,
                is_active = EXCLUDED.is_active,
                source_created_at = EXCLUDED.source_created_at,
                source_updated_at = EXCLUDED.source_updated_at,
                etl_loaded_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(sql)

        rows_affected = cursor.rowcount

        connection.commit()

        logger.info(
            "Product dimension load completed successfully. "
            "Rows affected: %s",
            rows_affected
        )

    except Exception as error:

        connection.rollback()

        logger.error(
            "Product dimension load failed: %s",
            error
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_products()