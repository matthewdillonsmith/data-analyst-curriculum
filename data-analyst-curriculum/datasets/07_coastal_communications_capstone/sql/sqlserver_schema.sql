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
    first_name NVARCHAR(21),
    last_name NVARCHAR(21),
    email NVARCHAR(42),
    phone NVARCHAR(22),
    join_date NVARCHAR(20),
    crm_status_cd NVARCHAR(20)
);

CREATE TABLE addresses (
    address_id BIGINT,
    member_id BIGINT,
    address_type NVARCHAR(20),
    street NVARCHAR(45),
    city NVARCHAR(31),
    state NVARCHAR(20),
    zipcode NVARCHAR(20),
    PRIMARY KEY (address_id)
);

CREATE TABLE accounts (
    account_id BIGINT,
    member_id BIGINT,
    service_address NVARCHAR(45),
    service_city NVARCHAR(33),
    service_state NVARCHAR(20),
    start_date NVARCHAR(20),
    end_date NVARCHAR(20),
    billing_status_cd NVARCHAR(20),
    PRIMARY KEY (account_id)
);

CREATE TABLE plan_history (
    plan_history_id BIGINT,
    account_id BIGINT,
    plan_cd NVARCHAR(21),
    effective_start NVARCHAR(20),
    effective_end NVARCHAR(20),
    PRIMARY KEY (plan_history_id)
);

CREATE TABLE bills (
    bill_id BIGINT,
    account_id BIGINT,
    billing_month NVARCHAR(20),
    bill_date NVARCHAR(20),
    service_amount FLOAT,
    tax_amount FLOAT,
    adjustment_amount FLOAT,
    total_due FLOAT,
    load_timestamp NVARCHAR(29),
    PRIMARY KEY (bill_id)
);

CREATE TABLE payments (
    payment_id BIGINT,
    bill_id BIGINT,
    account_id BIGINT,
    payment_date NVARCHAR(20),
    payment_amount FLOAT,
    load_timestamp NVARCHAR(29),
    PRIMARY KEY (payment_id)
);

CREATE TABLE adjustments (
    bill_id BIGINT,
    account_id BIGINT,
    adjustment_id BIGINT,
    adjustment_type_cd NVARCHAR(20),
    amount FLOAT,
    PRIMARY KEY (adjustment_id)
);

CREATE TABLE service_orders (
    service_order_id BIGINT,
    account_id BIGINT,
    order_type_cd NVARCHAR(20),
    created_timestamp NVARCHAR(29),
    status_cd NVARCHAR(20),
    PRIMARY KEY (service_order_id)
);

CREATE TABLE service_order_events (
    service_event_id BIGINT,
    service_order_id BIGINT,
    event_cd NVARCHAR(20),
    event_timestamp NVARCHAR(29),
    PRIMARY KEY (service_event_id)
);

CREATE TABLE devices (
    device_id BIGINT,
    account_id BIGINT,
    device_type_cd NVARCHAR(20),
    install_date NVARCHAR(20),
    PRIMARY KEY (device_id)
);

CREATE TABLE device_status_history (
    status_event_id BIGINT,
    device_id BIGINT,
    status_timestamp NVARCHAR(29),
    status_cd NVARCHAR(20),
    PRIMARY KEY (status_event_id)
);

CREATE TABLE outages (
    outage_id BIGINT,
    start_timestamp NVARCHAR(29),
    restore_timestamp NVARCHAR(29),
    cause_cd NVARCHAR(20),
    customers_affected BIGINT,
    PRIMARY KEY (outage_id)
);

CREATE TABLE account_balance_snapshots (
    snapshot_id BIGINT,
    snapshot_date NVARCHAR(20),
    account_id BIGINT,
    balance FLOAT,
    status_cd NVARCHAR(20),
    PRIMARY KEY (snapshot_id)
);
