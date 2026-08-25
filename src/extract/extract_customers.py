from psycopg2.extras import execute_batch

from src.utils.db_connection import (
    get_source_connection,
    get_target_connection,
)


BATCH_SIZE = 5_000


def extract_customers():
    source_connection = get_source_connection()
    source_cursor = source_connection.cursor()

    target_connection = get_target_connection()
    target_cursor = target_connection.cursor()

    try:
        # ---------------------------------------------------------
        # 1. Extract data from source database
        # ---------------------------------------------------------

        source_cursor.execute("""
            SELECT
                customer_id,
                customer_name,
                email,
                phone,
                city,
                state,
                customer_segment,
                created_at,
                updated_at
            FROM tbl_customers
            ORDER BY customer_id;
        """)

        customers = source_cursor.fetchall()

        print(f"Extracted {len(customers)} customers from source.")

        # ---------------------------------------------------------
        # 2. Clear staging table
        # ---------------------------------------------------------

        target_cursor.execute("""
            TRUNCATE TABLE staging.stg_customers;
        """)

        # ---------------------------------------------------------
        # 3. Load data into staging
        # ---------------------------------------------------------

        insert_query = """
            INSERT INTO staging.stg_customers (
                customer_id,
                customer_name,
                email,
                phone,
                city,
                state,
                customer_segment,
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
            customers,
            page_size=BATCH_SIZE
        )

        # ---------------------------------------------------------
        # 4. Commit target transaction
        # ---------------------------------------------------------

        target_connection.commit()

        print(
            f"Loaded {len(customers)} customers "
            "into staging.stg_customers."
        )

    except Exception as error:

        target_connection.rollback()

        print(f"ETL failed: {error}")

        raise

    finally:

        source_cursor.close()
        source_connection.close()

        target_cursor.close()
        target_connection.close()


if __name__ == "__main__":
    extract_customers()