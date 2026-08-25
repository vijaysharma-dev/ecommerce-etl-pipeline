# Ecommerce ETL Pipeline

An end-to-end ecommerce data engineering project built using Python, PostgreSQL, Docker, and Apache Airflow.

The project demonstrates a complete ETL workflow from source PostgreSQL databases into an analytics warehouse, including staging, dimensional modeling, fact tables, data-quality validation, orchestration, retries, and scheduled execution.

## Architecture

```text
Source PostgreSQL
       |
       v
Python ETL
       |
       v
Staging Layer
       |
       v
Analytics Warehouse
       |
       v
Data Quality Validation
       ^
       |
Apache Airflow
Tech Stack
Python
PostgreSQL 16
Apache Airflow 3.0.2
Docker
Docker Compose
psycopg2
SQL
Git / GitHub
Project Structure
etl-ecommerce-pipeline/
|
├── airflow/
│   └── dags/
│       └── ecommerce_etl_dag.py
|
├── sql/
│   └── load_dim_customer.sql
|
├── src/
│   ├── etl/
│   ├── extract/
│   ├── validation/
│   └── utils/
|
├── docker-compose.yml
├── .gitignore
├── README.md
└── .env
ETL Pipeline

The pipeline processes five major entities:

Customers
Source
  ↓
Extract
  ↓
staging.stg_customers
  ↓
Load
  ↓
analytics.dim_customer
  ↓
Validation

Validated count: 10,000 customers

Products
Source
  ↓
Extract
  ↓
staging.stg_products
  ↓
Load
  ↓
analytics.dim_product
  ↓
Validation

Validated count: 1,000 products

Locations
Source
  ↓
Extract
  ↓
staging.stg_locations
  ↓
Load
  ↓
analytics.dim_location
  ↓
Validation

Validated count: 20 locations

Orders

Orders depend on the customer and location dimensions.

Customer Validation ──┐
                      ├──> Extract Orders
Location Validation ──┘
                            ↓
                       Load Orders
                            ↓
                    Validate Orders

Validated count: 100,000 orders

Order Items

Order items depend on products and orders.

Product Validation ──┐
                     ├──> Extract Order Items
Order Validation ────┘
                           ↓
                    Load Order Items

Validated count: 250,437 order items

Analytics Warehouse
Dimensions
analytics.dim_customer
analytics.dim_product
analytics.dim_location
Facts
analytics.fact_order
analytics.fact_order_item

The warehouse uses surrogate keys for dimensions while maintaining source business keys for traceability.

Airflow

The complete ETL process is orchestrated using Apache Airflow.

DAG:

ecommerce_etl_dag

The DAG manages:

Extraction
Staging loads
Dimension loads
Fact loads
Data-quality validation
Task dependencies
Retries
Scheduled execution
Task Flow
Customers
Extract → Load → Validate
                    |
                    |
Locations            |
Extract → Load → Validate
                    |
                    v
              Extract Orders
                    |
               Load Orders
                    |
             Validate Orders
                    |
                    v
            Extract Order Items
                    |
             Load Order Items
Scheduling

Production schedule:

0 2 * * *

Timezone:

Asia/Kolkata

During development, automatic scheduling was tested using:

*/10 * * * *

The 10-minute schedule successfully verified automatic Airflow scheduler execution before returning to the final daily schedule.

Retry Handling

The pipeline supports Airflow task retries for transient failures.

This helps prevent temporary errors from immediately failing the entire workflow.

Data Quality

Validation compares source, staging, and analytics record counts.

Example:

Source Count
     ↓
Staging Count
     ↓
Analytics Count
     ↓
PASS / FAIL

Validated warehouse counts:

dim_customer       10,000
dim_product         1,000
dim_location           20
fact_order        100,000
fact_order_item   250,437
Docker Environment

The complete local environment runs using Docker Compose.

Services:

postgres-source
postgres-target
airflow

Ports:

Source PostgreSQL → 5433
Target PostgreSQL → 5434
Airflow           → 8081

Start the environment:

docker compose up -d

Check containers:

docker compose ps

Open Airflow:

http://localhost:8081
Environment Variables

Database credentials are stored locally in:

.env

The .env file is excluded from Git using .gitignore.

Example:

SOURCE_DB_HOST=
SOURCE_DB_PORT=
SOURCE_DB_NAME=
SOURCE_DB_USER=
SOURCE_DB_PASSWORD=

TARGET_DB_HOST=
TARGET_DB_PORT=
TARGET_DB_NAME=
TARGET_DB_USER=
TARGET_DB_PASSWORD=

Actual credentials should never be committed to GitHub.

Manual ETL Execution

Example extraction:

python -m src.extract.extract_customers

Example load:

python -m src.etl.load_customers

Example validation:

python -m src.validation.customer_quality

The complete pipeline is normally executed through Airflow.

Key Learning Areas

This project demonstrates practical experience with:

ETL pipeline development
Python data extraction
PostgreSQL
SQL
Staging architecture
Dimensional modeling
Fact and dimension tables
Surrogate keys
Upsert processing
Data-quality validation
Airflow DAG development
Airflow task dependencies
Airflow retries
Airflow scheduling
Docker containerization
Environment configuration
Git version control
Future Improvements
AWS deployment
External Airflow metadata database
Centralized monitoring
Failure notifications
Incremental extraction using timestamps
Additional data-quality checks
Unit and integration testing
CI/CD pipeline
Cloud secret management
Warehouse performance optimization