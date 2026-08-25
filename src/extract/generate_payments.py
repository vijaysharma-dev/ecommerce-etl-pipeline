import random
from decimal import Decimal

from psycopg2.extras import execute_batch

from src.utils.db_connection import get_source_connection


BATCH_SIZE = 5_000

PAYMENT_METHODS = [
    "UPI",
    "CARD",
    "NET_BANKING",
    "WALLET",
    "COD",
]

PAYMENT_STATUSES = [
    "SUCCESS",
    "PENDING",
    "FAILED",
]


def generate_payments():
    connection = get_source_connection()
    cursor = connection.cursor()

    # Get orders and their final amounts
    cursor.execute("""
        SELECT
            order_id,
            total_amount,
            order_date,
            order_status
        FROM tbl_orders
        ORDER BY order_id;
    """)

    orders = cursor.fetchall()

    payments = []

    for order_id, total_amount, order_date, order_status in orders:

        # Cancelled orders are more likely to have failed/pending payments
        if order_status == "CANCELLED":
            payment_status = random.choices(
                PAYMENT_STATUSES,
                weights=[30, 20, 50],
                k=1
            )[0]
        else:
            payment_status = random.choices(
                PAYMENT_STATUSES,
                weights=[92, 5, 3],
                k=1
            )[0]

        payment_method = random.choice(PAYMENT_METHODS)

        amount = Decimal(str(total_amount))

        payments.append(
            (
                order_id,
                payment_method,
                payment_status,
                amount,
                order_date,
            )
        )

        if len(payments) >= BATCH_SIZE:

            insert_payments(cursor, payments)

            payments.clear()

    # Insert remaining records
    if payments:
        insert_payments(cursor, payments)

    connection.commit()

    cursor.close()
    connection.close()


def insert_payments(cursor, payments):

    insert_query = """
        INSERT INTO tbl_payments (
            order_id,
            payment_method,
            payment_status,
            amount,
            payment_date
        )
        VALUES (%s, %s, %s, %s, %s);
    """

    execute_batch(
        cursor,
        insert_query,
        payments,
        page_size=BATCH_SIZE
    )


if __name__ == "__main__":
    generate_payments()

    print("Payment generation completed.")