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
    customer_name NVARCHAR(43),
    billing_state NVARCHAR(20),
    active_flag BIGINT,
    created_date NVARCHAR(20),
    PRIMARY KEY (customer_id)
);

CREATE TABLE customer_master (
    customer_id BIGINT,
    customer_name NVARCHAR(43),
    crm_state NVARCHAR(20),
    mailing_address NVARCHAR(46),
    mailing_city NVARCHAR(33)
);

CREATE TABLE warehouses (
    warehouse_id BIGINT,
    warehouse_name NVARCHAR(32),
    city NVARCHAR(29),
    state NVARCHAR(20),
    PRIMARY KEY (warehouse_id)
);

CREATE TABLE drivers (
    driver_id BIGINT,
    driver_name NVARCHAR(29),
    home_warehouse_id BIGINT,
    hire_date NVARCHAR(20),
    active_flag BIGINT,
    PRIMARY KEY (driver_id)
);

CREATE TABLE vehicles (
    vehicle_id BIGINT,
    vin_last8 NVARCHAR(20),
    home_warehouse_id BIGINT,
    model_year BIGINT,
    vehicle_type NVARCHAR(20),
    PRIMARY KEY (vehicle_id)
);

CREATE TABLE shipments (
    shipment_id BIGINT,
    customer_id BIGINT,
    origin_warehouse_id BIGINT,
    driver_id FLOAT,
    vehicle_id BIGINT,
    pickup_timestamp NVARCHAR(29),
    promised_delivery_timestamp NVARCHAR(29),
    actual_delivery_timestamp NVARCHAR(29),
    status NVARCHAR(20),
    weight_lbs FLOAT,
    PRIMARY KEY (shipment_id)
);

CREATE TABLE delivery_events (
    delivery_event_id BIGINT,
    shipment_id BIGINT,
    event_type NVARCHAR(21),
    event_timestamp NVARCHAR(29),
    PRIMARY KEY (delivery_event_id)
);

CREATE TABLE fuel_transactions (
    fuel_transaction_id BIGINT,
    vehicle NVARCHAR(20),
    transaction_timestamp NVARCHAR(29),
    gallons FLOAT,
    price_per_gallon FLOAT,
    total_cost FLOAT
);

CREATE TABLE gps_events (
    gps_event_id BIGINT,
    vehicle_id NVARCHAR(20),
    timestamp NVARCHAR(29),
    latitude FLOAT,
    longitude FLOAT,
    speed_mph FLOAT,
    PRIMARY KEY (gps_event_id)
);
