import random
from datetime import datetime, timedelta

from faker import Faker
from psycopg2.extras import execute_batch

from src.utils.db_connection import get_source_connection


fake = Faker("en_IN")

ORDER_COUNT = 100_000

ORDER_STATUSES = [
    "PLACED",
    "CONFIRMED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
]

PAYMENT_STATUSES = [
    "SUCCESS",
    "PENDING",
    "FAILED",
]

START_DATE = datetime.now() - timedelta(days=365)
END_DATE = datetime.now()


def generate_orders():
    connection = get_source_connection()
    cursor = connection.cursor()

    # Load existing customer IDs
    cursor.execute("""
        SELECT customer_id
        FROM tbl_customers;
    """)
    customer_ids = [row[0] for row in cursor.fetchall()]

    # Load existing location IDs
    cursor.execute("""
        SELECT location_id
        FROM tbl_locations;
    """)
    location_ids = [row[0] for row in cursor.fetchall()]

    orders = []

    for _ in range(ORDER_COUNT):
        customer_id = random.choice(customer_ids)
        location_id = random.choice(location_ids)

        order_date = fake.date_time_between(
            start_date=START_DATE,
            end_date=END_DATE
        )

        order_status = random.choices(
            ORDER_STATUSES,
            weights=[10, 10, 10, 65, 5],
            k=1
        )[0]

        payment_status = random.choices(
            PAYMENT_STATUSES,
            weights=[90, 7, 3],
            k=1
        )[0]

        subtotal = round(random.uniform(200, 15000), 2)

        discount_amount = round(
            subtotal * random.uniform(0, 0.20),
            2
        )

        tax_amount = round(
            (subtotal - discount_amount) * 0.18,
            2
        )

        shipping_amount = round(
            random.choice([0, 0, 0, 40, 60, 80]),
            2
        )

        total_amount = round(
            subtotal
            - discount_amount
            + tax_amount
            + shipping_amount,
            2
        )

        orders.append(
            (
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
            )
        )

    insert_query = """
        INSERT INTO tbl_orders (
            customer_id,
            location_id,
            order_date,
            order_status,
            payment_status,
            subtotal,
            discount_amount,
            tax_amount,
            shipping_amount,
            total_amount
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        );
    """

    execute_batch(
        cursor,
        insert_query,
        orders,
        page_size=5_000
    )

    connection.commit()

    print(f"Inserted {len(orders)} orders.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    generate_orders()