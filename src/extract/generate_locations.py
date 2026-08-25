import random

from faker import Faker

from src.utils.db_connection import get_source_connection


fake = Faker("en_IN")


def generate_locations():
    locations = []

    cities = [
        ("Mumbai", "Maharashtra", "West"),
        ("Pune", "Maharashtra", "West"),
        ("Nashik", "Maharashtra", "West"),
        ("Nagpur", "Maharashtra", "West"),
        ("Ahmedabad", "Gujarat", "West"),
        ("Surat", "Gujarat", "West"),
        ("Bengaluru", "Karnataka", "South"),
        ("Chennai", "Tamil Nadu", "South"),
        ("Hyderabad", "Telangana", "South"),
        ("Kochi", "Kerala", "South"),
        ("Delhi", "Delhi", "North"),
        ("Noida", "Uttar Pradesh", "North"),
        ("Gurugram", "Haryana", "North"),
        ("Jaipur", "Rajasthan", "North"),
        ("Lucknow", "Uttar Pradesh", "North"),
        ("Kolkata", "West Bengal", "East"),
        ("Bhubaneswar", "Odisha", "East"),
        ("Patna", "Bihar", "East"),
        ("Ranchi", "Jharkhand", "East"),
        ("Guwahati", "Assam", "East"),
    ]

    for city, state, region in cities:
        locations.append(
            (
                city,
                state,
                region,
                fake.postcode(),
            )
        )

    return locations


def insert_locations(locations):
    connection = get_source_connection()
    cursor = connection.cursor()

    insert_query = """
        INSERT INTO tbl_locations (
            city,
            state,
            region,
            pincode
        )
        VALUES (%s, %s, %s, %s);
    """

    cursor.executemany(insert_query, locations)

    connection.commit()

    print(f"Inserted {cursor.rowcount} locations.")

    cursor.close()
    connection.close()


def main():
    locations = generate_locations()
    insert_locations(locations)


if __name__ == "__main__":
    main()