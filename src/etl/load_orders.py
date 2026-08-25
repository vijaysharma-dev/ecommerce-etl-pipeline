from src.utils.db_connection import get_target_connection
from src.utils.logger import get_logger


logger = get_logger(__name__)


def load_orders():
    connection = get_target_connection()
    cursor = connection.cursor()

    try:
        logger.info("Order fact load started.")

        sql = """
            INSERT INTO analytics.fact_order (
                order_id,
                customer_key,
                location_key,
                order_date,
                order_status,
                payment_status,
                subtotal,
                discount_amount,
                tax_amount,
                shipping_amount,
                total_amount,
                source_created_at,
                source_updated_at,
                etl_loaded_at
            )
            SELECT
                s.order_id,
                c.customer_key,
                l.location_key,
                s.order_date,
                s.order_status,
                s.payment_status,
                s.subtotal,
                s.discount_amount,
                s.tax_amount,
                s.shipping_amount,
                s.total_amount,
                s.source_created_at,
                s.source_updated_at,
                CURRENT_TIMESTAMP
                FROM staging.stg_orders s
                INNER JOIN analytics.dim_customer c
                    ON s.customer_id = c.customer_id
                INNER JOIN analytics.dim_location l
                    ON s.location_id = l.location_id

            ON CONFLICT (order_id)
            DO UPDATE SET
                customer_key = EXCLUDED.customer_key,
                location_key = EXCLUDED.location_key,
                order_date = EXCLUDED.order_date,
                order_status = EXCLUDED.order_status,
                payment_status = EXCLUDED.payment_status,
                subtotal = EXCLUDED.subtotal,
                discount_amount = EXCLUDED.discount_amount,
                tax_amount = EXCLUDED.tax_amount,
                shipping_amount = EXCLUDED.shipping_amount,
                total_amount = EXCLUDED.total_amount,
                source_created_at = EXCLUDED.source_created_at,
                source_updated_at = EXCLUDED.source_updated_at,
                etl_loaded_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(sql)

        rows_affected = cursor.rowcount

        connection.commit()

        logger.info(
            "Order fact load completed successfully. "
            "Rows affected: %s",
            rows_affected
        )

    except Exception as error:

        connection.rollback()

        logger.error(
            "Order fact load failed: %s",
            error
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_orders()