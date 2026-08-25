import random

from faker import Faker

from src.utils.db_connection import get_source_connection


fake = Faker("en_IN")

CUSTOMER_COUNT = 10_000

CUSTOMER_SEGMENTS = [
    "Premium",
    "Regular",
    "Occasional",
]


def generate_customers():
    connection = get_source_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT location_id, city, state
        FROM tbl_locations
        ORDER BY location_id;
    """)

    locations = cursor.fetchall()

    customers = []

    for _ in range(CUSTOMER_COUNT):
        location_id, city, state = random.choice(locations)

        customers.append(
            (
                fake.name(),
                fake.unique.email(),
                fake.phone_number()[:20],
                city,
                state,
                random.choice(CUSTOMER_SEGMENTS),
            )
        )

    insert_query = """
        INSERT INTO tbl_customers (
            customer_name,
            email,
            phone,
            city,
            state,
            customer_segment
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    cursor.executemany(insert_query, customers)

    connection.commit()

    print(f"Inserted {cursor.rowcount} customers.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    generate_customers()