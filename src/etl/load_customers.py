from src.utils.db_connection import get_target_connection
from src.utils.logger import get_logger


logger = get_logger(__name__)


def load_customers():
    connection = get_target_connection()
    cursor = connection.cursor()

    try:
        logger.info("Customer dimension load started.")

        sql = """
            INSERT INTO analytics.dim_customer (
                customer_id,
                customer_name,
                email,
                phone,
                city,
                state,
                customer_segment,
                source_created_at,
                source_updated_at,
                etl_loaded_at
            )
            SELECT
                customer_id,
                customer_name,
                email,
                phone,
                city,
                state,
                customer_segment,
                source_created_at,
                source_updated_at,
                CURRENT_TIMESTAMP
            FROM staging.stg_customers

            ON CONFLICT (customer_id)
            DO UPDATE SET
                customer_name = EXCLUDED.customer_name,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                customer_segment = EXCLUDED.customer_segment,
                source_created_at = EXCLUDED.source_created_at,
                source_updated_at = EXCLUDED.source_updated_at,
                etl_loaded_at = CURRENT_TIMESTAMP;
        """

        cursor.execute(sql)

        rows_affected = cursor.rowcount

        connection.commit()

        logger.info(
                "Customer dimension load completed successfully. "
                "Rows affected: %s",
                rows_affected
            )

    except Exception as error:

        connection.rollback()

        logger.error(
            "Customer dimension load failed: %s",
            error
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_customers()