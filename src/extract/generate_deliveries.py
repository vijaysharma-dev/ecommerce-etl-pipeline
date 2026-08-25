import random
from datetime import timedelta

from psycopg2.extras import execute_batch

from src.utils.db_connection import get_source_connection


BATCH_SIZE = 5_000

DELIVERY_PARTNERS = [
    "FastTrack Logistics",
    "QuickShip",
    "UrbanExpress",
    "MetroDelivery",
    "PrimeCourier",
]

DELIVERY_STATUSES = [
    "DELIVERED",
    "IN_TRANSIT",
    "CANCELLED",
]


def generate_deliveries():
    connection = get_source_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            order_id,
            order_date,
            order_status
        FROM tbl_orders
        ORDER BY order_id;
    """)

    orders = cursor.fetchall()

    insert_query = """
        INSERT INTO tbl_deliveries (
            order_id,
            delivery_partner,
            promised_delivery_at,
            actual_delivery_at,
            delivery_status
        )
        VALUES (%s, %s, %s, %s, %s);
    """

    batch = []
    total_deliveries = 0

    for order_id, order_date, order_status in orders:

        # Cancelled orders generally do not require a delivery.
        if order_status == "CANCELLED":
            delivery_status = "CANCELLED"
            promised_delivery_at = order_date + timedelta(
                hours=random.randint(4, 24)
            )
            actual_delivery_at = None

        else:
            delivery_status = random.choices(
                DELIVERY_STATUSES,
                weights=[90, 7, 3],
                k=1
            )[0]

            promised_delivery_at = order_date + timedelta(
                hours=random.randint(4, 48)
            )

            if delivery_status == "DELIVERED":

                # Mostly on-time, with some delayed deliveries
                if random.random() < 0.85:
                    actual_delivery_at = promised_delivery_at - timedelta(
                        minutes=random.randint(5, 120)
                    )
                else:
                    actual_delivery_at = promised_delivery_at + timedelta(
                        minutes=random.randint(10, 360)
                    )

            elif delivery_status == "IN_TRANSIT":
                actual_delivery_at = None

            else:
                actual_delivery_at = None

        delivery_partner = random.choice(DELIVERY_PARTNERS)

        batch.append(
            (
                order_id,
                delivery_partner,
                promised_delivery_at,
                actual_delivery_at,
                delivery_status,
            )
        )

        if len(batch) >= BATCH_SIZE:

            execute_batch(
                cursor,
                insert_query,
                batch,
                page_size=BATCH_SIZE
            )

            total_deliveries += len(batch)
            batch.clear()

    if batch:

        execute_batch(
            cursor,
            insert_query,
            batch,
            page_size=BATCH_SIZE
        )

        total_deliveries += len(batch)

    connection.commit()

    print(f"Inserted {total_deliveries} deliveries.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    generate_deliveries()