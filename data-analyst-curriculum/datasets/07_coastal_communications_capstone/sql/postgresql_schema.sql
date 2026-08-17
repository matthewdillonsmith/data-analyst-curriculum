DROP TABLE IF EXISTS account_balance_snapshots;
DROP TABLE IF EXISTS outages;
DROP TABLE IF EXISTS device_status_history;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS service_order_events;
DROP TABLE IF EXISTS service_orders;
DROP TABLE IF EXISTS adjustments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS plan_history;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    member_id BIGINT,
    first_name VARCHAR(21),
    last_name VARCHAR(21),
    email VARCHAR(42),
    phone VARCHAR(22),
    join_date VARCHAR(20),
    crm_status_cd VARCHAR(20)
);

CREATE TABLE addresses (
    address_id BIGINT,
    member_id BIGINT,
    address_type VARCHAR(20),
    street VARCHAR(45),
    city VARCHAR(31),
    state VARCHAR(20),
    zipcode VARCHAR(20),
    PRIMARY KEY (address_id)
);

CREATE TABLE accounts (
    account_id BIGINT,
    member_id BIGINT,
    service_address VARCHAR(45),
    service_city VARCHAR(33),
    service_state VARCHAR(20),
    start_date VARCHAR(20),
    end_date VARCHAR(20),
    billing_status_cd VARCHAR(20),
    PRIMARY KEY (account_id)
);

CREATE TABLE plan_history (
    plan_history_id BIGINT,
    account_id BIGINT,
    plan_cd VARCHAR(21),
    effective_start VARCHAR(20),
    effective_end VARCHAR(20),
    PRIMARY KEY (plan_history_id)
);

CREATE TABLE bills (
    bill_id BIGINT,
    account_id BIGINT,
    billing_month VARCHAR(20),
    bill_date VARCHAR(20),
    service_amount DOUBLE PRECISION,
    tax_amount DOUBLE PRECISION,
    adjustment_amount DOUBLE PRECISION,
    total_due DOUBLE PRECISION,
    load_timestamp VARCHAR(29),
    PRIMARY KEY (bill_id)
);

CREATE TABLE payments (
    payment_id BIGINT,
    bill_id BIGINT,
    account_id BIGINT,
    payment_date VARCHAR(20),
    payment_amount DOUBLE PRECISION,
    load_timestamp VARCHAR(29),
    PRIMARY KEY (payment_id)
);

CREATE TABLE adjustments (
    bill_id BIGINT,
    account_id BIGINT,
    adjustment_id BIGINT,
    adjustment_type_cd VARCHAR(20),
    amount DOUBLE PRECISION,
    PRIMARY KEY (adjustment_id)
);

CREATE TABLE service_orders (
    service_order_id BIGINT,
    account_id BIGINT,
    order_type_cd VARCHAR(20),
    created_timestamp VARCHAR(29),
    status_cd VARCHAR(20),
    PRIMARY KEY (service_order_id)
);

CREATE TABLE service_order_events (
    service_event_id BIGINT,
    service_order_id BIGINT,
    event_cd VARCHAR(20),
    event_timestamp VARCHAR(29),
    PRIMARY KEY (service_event_id)
);

CREATE TABLE devices (
    device_id BIGINT,
    account_id BIGINT,
    device_type_cd VARCHAR(20),
    install_date VARCHAR(20),
    PRIMARY KEY (device_id)
);

CREATE TABLE device_status_history (
    status_event_id BIGINT,
    device_id BIGINT,
    status_timestamp VARCHAR(29),
    status_cd VARCHAR(20),
    PRIMARY KEY (status_event_id)
);

CREATE TABLE outages (
    outage_id BIGINT,
    start_timestamp VARCHAR(29),
    restore_timestamp VARCHAR(29),
    cause_cd VARCHAR(20),
    customers_affected BIGINT,
    PRIMARY KEY (outage_id)
);

CREATE TABLE account_balance_snapshots (
    snapshot_id BIGINT,
    snapshot_date VARCHAR(20),
    account_id BIGINT,
    balance DOUBLE PRECISION,
    status_cd VARCHAR(20),
    PRIMARY KEY (snapshot_id)
);
