from src.utils.db_connection import get_target_connection
from src.utils.logger import get_logger


logger = get_logger(__name__)


def load_order_items():
    connection = get_target_connection()
    cursor = connection.cursor()

    try:
        logger.info("Order item fact load started.")

        sql = """
            INSERT INTO analytics.fact_order_item (
                order_item_id,
                order_id,
                product_key,
                quantity,
                unit_price,
                discount_amount,
                line_amount,
                source_created_at,
                source_updated_at,
                etl_loaded_at
            )
            SELECT
                s.order_item_id,
                s.order_id,
                p.product_key,
                s.quantity,
                s.unit_price,
                s.discount_amount,
                s.line_amount,
                s.source_created_at,
                s.source_updated_at,
                CURRENT_TIMESTAMP
            FROM staging.stg_order_items s
            INNER JOIN analytics.dim_product p
                ON s.product_id = p.product_id
            INNER JOIN analytics.fact_order o
                ON s.order_id = o.order_id

            ON CONFLICT (order_item_id)
            DO UPDATE SET
                order_id = EXCLUDED.order_id,
                product_key = EXCLUDED.product_key,
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price,
                discount_amount = EXCLUDED.discount_amount,
                line_amount = EXCLUDED.line_amount,
                source_created_at = EXCLUDED.source_created_at,
                source_updated_at = EXCLUDED.source_updated_at,
                etl_loaded_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(sql)

        rows_affected = cursor.rowcount

        connection.commit()

        logger.info(
            "Order item fact load completed successfully. "
            "Rows affected: %s",
            rows_affected
        )

    except Exception as error:

        connection.rollback()

        logger.error(
            "Order item fact load failed: %s",
            error
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_order_items()