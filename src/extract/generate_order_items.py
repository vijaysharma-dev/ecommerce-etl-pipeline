import random
from decimal import Decimal

from psycopg2.extras import execute_batch

from src.utils.db_connection import get_source_connection


BATCH_SIZE = 5_000


def generate_order_items():
    connection = get_source_connection()
    cursor = connection.cursor()

    # Load existing order IDs
    cursor.execute("""
        SELECT order_id
        FROM tbl_orders
        ORDER BY order_id;
    """)
    order_ids = [row[0] for row in cursor.fetchall()]

    # Load active product IDs and prices
    cursor.execute("""
        SELECT product_id, unit_price
        FROM tbl_products
        WHERE is_active = TRUE;
    """)
    products = cursor.fetchall()

    insert_query = """
        INSERT INTO tbl_order_items (
            order_id,
            product_id,
            quantity,
            unit_price,
            discount_amount,
            line_amount
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    total_items = 0
    batch = []

    for order_id in order_ids:

        # Each order contains 1–4 different products
        item_count = random.randint(1, 4)

        selected_products = random.sample(
            products,
            min(item_count, len(products))
        )

        for product_id, unit_price in selected_products:

            quantity = random.randint(1, 5)

            # Use Decimal for financial calculations
            discount_rate = Decimal(
                str(random.uniform(0, 0.15))
            )

            discount_amount = (
                unit_price
                * quantity
                * discount_rate
            ).quantize(
                Decimal("0.01")
            )

            line_amount = (
                (unit_price * quantity)
                - discount_amount
            ).quantize(
                Decimal("0.01")
            )

            batch.append(
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount_amount,
                    line_amount,
                )
            )

            # Insert records in batches
            if len(batch) >= BATCH_SIZE:

                execute_batch(
                    cursor,
                    insert_query,
                    batch,
                    page_size=BATCH_SIZE
                )

                total_items += len(batch)
                batch.clear()

    # Insert remaining records
    if batch:

        execute_batch(
            cursor,
            insert_query,
            batch,
            page_size=BATCH_SIZE
        )

        total_items += len(batch)

    connection.commit()

    print(f"Inserted {total_items} order items.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    generate_order_items()