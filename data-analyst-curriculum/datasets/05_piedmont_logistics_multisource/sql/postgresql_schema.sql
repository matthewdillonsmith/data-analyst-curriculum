DROP TABLE IF EXISTS gps_events;
DROP TABLE IF EXISTS fuel_transactions;
DROP TABLE IF EXISTS delivery_events;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS customer_master;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id BIGINT,
    customer_name VARCHAR(43),
    billing_state VARCHAR(20),
    active_flag BIGINT,
    created_date VARCHAR(20),
    PRIMARY KEY (customer_id)
);

CREATE TABLE customer_master (
    customer_id BIGINT,
    customer_name VARCHAR(43),
    crm_state VARCHAR(20),
    mailing_address VARCHAR(46),
    mailing_city VARCHAR(33)
);

CREATE TABLE warehouses (
    warehouse_id BIGINT,
    warehouse_name VARCHAR(32),
    city VARCHAR(29),
    state VARCHAR(20),
    PRIMARY KEY (warehouse_id)
);

CREATE TABLE drivers (
    driver_id BIGINT,
    driver_name VARCHAR(29),
    home_warehouse_id BIGINT,
    hire_date VARCHAR(20),
    active_flag BIGINT,
    PRIMARY KEY (driver_id)
);

CREATE TABLE vehicles (
    vehicle_id BIGINT,
    vin_last8 VARCHAR(20),
    home_warehouse_id BIGINT,
    model_year BIGINT,
    vehicle_type VARCHAR(20),
    PRIMARY KEY (vehicle_id)
);

CREATE TABLE shipments (
    shipment_id BIGINT,
    customer_id BIGINT,
    origin_warehouse_id BIGINT,
    driver_id DOUBLE PRECISION,
    vehicle_id BIGINT,
    pickup_timestamp VARCHAR(29),
    promised_delivery_timestamp VARCHAR(29),
    actual_delivery_timestamp VARCHAR(29),
    status VARCHAR(20),
    weight_lbs DOUBLE PRECISION,
    PRIMARY KEY (shipment_id)
);

CREATE TABLE delivery_events (
    delivery_event_id BIGINT,
    shipment_id BIGINT,
    event_type VARCHAR(21),
    event_timestamp VARCHAR(29),
    PRIMARY KEY (delivery_event_id)
);

CREATE TABLE fuel_transactions (
    fuel_transaction_id BIGINT,
    vehicle VARCHAR(20),
    transaction_timestamp VARCHAR(29),
    gallons DOUBLE PRECISION,
    price_per_gallon DOUBLE PRECISION,
    total_cost DOUBLE PRECISION
);

CREATE TABLE gps_events (
    gps_event_id BIGINT,
    vehicle_id VARCHAR(20),
    timestamp VARCHAR(29),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    speed_mph DOUBLE PRECISION,
    PRIMARY KEY (gps_event_id)
);
