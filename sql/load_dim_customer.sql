INSERT INTO analytics.dim_customer (
    customer_id,
    customer_name,
    email,
    phone,
    city,
    state,
    customer_segment,
    source_created_at,
    source_updated_at,
    etl_loaded_at
)
SELECT
    customer_id,
    customer_name,
    email,
    phone,
    city,
    state,
    customer_segment,
    source_created_at,
    source_updated_at,
    CURRENT_TIMESTAMP
FROM staging.stg_customers
ON CONFLICT (customer_id)
DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    customer_segment = EXCLUDED.customer_segment,
    source_created_at = EXCLUDED.source_created_at,
    source_updated_at = EXCLUDED.source_updated_at,
    etl_loaded_at = CURRENT_TIMESTAMP;