from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


# ---------------------------------------------------------
# Import existing ETL functions
# ---------------------------------------------------------

from src.extract.extract_customers import extract_customers
from src.extract.extract_products import extract_products
from src.extract.extract_locations import extract_locations
from src.extract.extract_orders import extract_orders
from src.extract.extract_order_items import extract_order_items

from src.etl.load_customers import load_customers
from src.etl.load_products import load_products
from src.etl.load_locations import load_locations
from src.etl.load_orders import load_orders
from src.etl.load_order_items import load_order_items

from src.validation.customer_quality import validate_customer_data
from src.validation.product_quality import validate_product_data
from src.validation.location_quality import validate_location_data
from src.validation.order_quality import validate_order_data


# ---------------------------------------------------------
# Default task configuration
# ---------------------------------------------------------

default_args = {
    "owner": "vijay",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


# ---------------------------------------------------------
# DAG definition
# ---------------------------------------------------------

with DAG(
    dag_id="ecommerce_etl_dag",
    description="End-to-end ecommerce ETL pipeline",
    start_date=datetime(2026, 8, 25),
    schedule="0 2 * * *",
    catchup=False,
    default_args=default_args,
    tags=["ecommerce", "etl", "postgres"],
) as dag:

    # -----------------------------------------------------
    # CUSTOMER PIPELINE
    # -----------------------------------------------------

    extract_customers_task = PythonOperator(
        task_id="extract_customers",
        python_callable=extract_customers,
    )

    load_customers_task = PythonOperator(
        task_id="load_customers",
        python_callable=load_customers,
    )

    validate_customers_task = PythonOperator(
        task_id="validate_customers",
        python_callable=validate_customer_data,
    )

    # -----------------------------------------------------
    # PRODUCT PIPELINE
    # -----------------------------------------------------

    extract_products_task = PythonOperator(
        task_id="extract_products",
        python_callable=extract_products,
    )

    load_products_task = PythonOperator(
        task_id="load_products",
        python_callable=load_products,
    )

    validate_products_task = PythonOperator(
        task_id="validate_products",
        python_callable=validate_product_data,
    )

    # -----------------------------------------------------
    # LOCATION PIPELINE
    # -----------------------------------------------------

    extract_locations_task = PythonOperator(
        task_id="extract_locations",
        python_callable=extract_locations,
    )

    load_locations_task = PythonOperator(
        task_id="load_locations",
        python_callable=load_locations,
    )

    validate_locations_task = PythonOperator(
        task_id="validate_locations",
        python_callable=validate_location_data,
    )

    # -----------------------------------------------------
    # ORDER PIPELINE
    # -----------------------------------------------------

    extract_orders_task = PythonOperator(
        task_id="extract_orders",
        python_callable=extract_orders,
    )

    load_orders_task = PythonOperator(
        task_id="load_orders",
        python_callable=load_orders,
    )

    validate_orders_task = PythonOperator(
        task_id="validate_orders",
        python_callable=validate_order_data,
    )

    # -----------------------------------------------------
    # ORDER ITEM PIPELINE
    # -----------------------------------------------------

    extract_order_items_task = PythonOperator(
        task_id="extract_order_items",
        python_callable=extract_order_items,
    )

    load_order_items_task = PythonOperator(
        task_id="load_order_items",
        python_callable=load_order_items,
    )

    # -----------------------------------------------------
    # DEPENDENCIES
    # -----------------------------------------------------

    # Customer
    extract_customers_task >> load_customers_task >> validate_customers_task

    # Product
    extract_products_task >> load_products_task >> validate_products_task

    # Location
    extract_locations_task >> load_locations_task >> validate_locations_task

    # Orders require:
    # 1. Customer dimension
    # 2. Location dimension
    [
        validate_customers_task,
        validate_locations_task,
    ] >> extract_orders_task

    extract_orders_task >> load_orders_task >> validate_orders_task

    # Order items require:
    # 1. Product dimension
    # 2. Orders
    [
        validate_products_task,
        validate_orders_task,
    ] >> extract_order_items_task

    extract_order_items_task >> load_order_items_task