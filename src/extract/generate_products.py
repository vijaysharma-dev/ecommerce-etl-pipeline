import random

from faker import Faker

from src.utils.db_connection import get_source_connection


fake = Faker("en_IN")

PRODUCT_COUNT = 1_000

PRODUCT_CATALOG = {
    "Electronics": [
        "Smartphone",
        "Laptop",
        "Headphones",
        "Smartwatch",
        "Tablet",
    ],
    "Home & Kitchen": [
        "Mixer Grinder",
        "Air Fryer",
        "Cookware Set",
        "Water Bottle",
        "Storage Container",
    ],
    "Grocery": [
        "Rice",
        "Wheat Flour",
        "Cooking Oil",
        "Dal",
        "Spices",
    ],
    "Beauty": [
        "Face Wash",
        "Shampoo",
        "Moisturizer",
        "Sunscreen",
        "Body Lotion",
    ],
    "Sports": [
        "Cricket Bat",
        "Football",
        "Running Shoes",
        "Yoga Mat",
        "Tennis Racket",
    ],
}

BRANDS = [
    "Nova",
    "UrbanMart",
    "Prime",
    "FreshChoice",
    "DailyNeeds",
    "TechPro",
    "HomePlus",
    "ActiveLife",
]


def generate_products():
    products = []

    for _ in range(PRODUCT_COUNT):
        category = random.choice(list(PRODUCT_CATALOG.keys()))
        subcategory = random.choice(PRODUCT_CATALOG[category])
        brand = random.choice(BRANDS)

        unit_price = round(random.uniform(50, 15000), 2)

        cost_price = round(
            unit_price * random.uniform(0.55, 0.85),
            2
        )

        product_name = f"{brand} {subcategory} {fake.word().title()}"

        products.append(
            (
                product_name,
                category,
                subcategory,
                brand,
                unit_price,
                cost_price,
                random.random() > 0.05,
            )
        )

    return products


def insert_products(products):
    connection = get_source_connection()
    cursor = connection.cursor()

    insert_query = """
        INSERT INTO tbl_products (
            product_name,
            category,
            subcategory,
            brand,
            unit_price,
            cost_price,
            is_active
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    cursor.executemany(insert_query, products)

    connection.commit()

    print(f"Inserted {cursor.rowcount} products.")

    cursor.close()
    connection.close()


def main():
    products = generate_products()
    insert_products(products)


if __name__ == "__main__":
    main()