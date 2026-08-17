DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS work_order_parts;
DROP TABLE IF EXISTS parts;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS work_order_events;
DROP TABLE IF EXISTS technician_assignments;
DROP TABLE IF EXISTS work_orders;
DROP TABLE IF EXISTS service_types;
DROP TABLE IF EXISTS technicians;
DROP TABLE IF EXISTS service_locations;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id BIGINT,
    customer_name NVARCHAR(34),
    phone NVARCHAR(22),
    email NVARCHAR(42),
    state NVARCHAR(20),
    customer_since NVARCHAR(20),
    PRIMARY KEY (customer_id)
);

CREATE TABLE service_locations (
    service_location_id BIGINT,
    customer_id BIGINT,
    street NVARCHAR(45),
    city NVARCHAR(32),
    state NVARCHAR(20),
    zipcode NVARCHAR(20),
    PRIMARY KEY (service_location_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE technicians (
    technician_id BIGINT,
    technician_name NVARCHAR(31),
    trade NVARCHAR(20),
    hire_date NVARCHAR(20),
    active_flag BIGINT,
    PRIMARY KEY (technician_id)
);

CREATE TABLE service_types (
    service_type_id BIGINT,
    service_type_name NVARCHAR(37),
    target_hours BIGINT,
    PRIMARY KEY (service_type_id)
);

CREATE TABLE work_orders (
    work_order_id BIGINT,
    service_location_id BIGINT,
    service_type_id BIGINT,
    created_timestamp NVARCHAR(29),
    status NVARCHAR(20),
    priority NVARCHAR(20),
    reported_channel NVARCHAR(20),
    PRIMARY KEY (work_order_id),
    FOREIGN KEY (service_location_id) REFERENCES service_locations (service_location_id),
    FOREIGN KEY (service_type_id) REFERENCES service_types (service_type_id)
);

CREATE TABLE technician_assignments (
    assignment_id BIGINT,
    work_order_id BIGINT,
    technician_id BIGINT,
    assigned_timestamp NVARCHAR(29),
    PRIMARY KEY (assignment_id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders (work_order_id),
    FOREIGN KEY (technician_id) REFERENCES technicians (technician_id)
);

CREATE TABLE work_order_events (
    event_id BIGINT,
    work_order_id BIGINT,
    event_type NVARCHAR(20),
    event_timestamp NVARCHAR(29),
    source_system NVARCHAR(20),
    PRIMARY KEY (event_id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders (work_order_id)
);

CREATE TABLE appointments (
    appointment_id BIGINT,
    work_order_id BIGINT,
    scheduled_start NVARCHAR(29),
    appointment_status NVARCHAR(20),
    PRIMARY KEY (appointment_id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders (work_order_id)
);

CREATE TABLE parts (
    part_id BIGINT,
    part_name NVARCHAR(27),
    unit_cost FLOAT,
    PRIMARY KEY (part_id)
);

CREATE TABLE work_order_parts (
    work_order_part_id BIGINT,
    work_order_id BIGINT,
    part_id BIGINT,
    quantity BIGINT,
    PRIMARY KEY (work_order_part_id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders (work_order_id),
    FOREIGN KEY (part_id) REFERENCES parts (part_id)
);

CREATE TABLE invoices (
    invoice_id BIGINT,
    work_order_id BIGINT,
    invoice_date NVARCHAR(20),
    labor_amount FLOAT,
    parts_amount FLOAT,
    invoice_total FLOAT,
    PRIMARY KEY (invoice_id),
    FOREIGN KEY (work_order_id) REFERENCES work_orders (work_order_id)
);

CREATE TABLE payments (
    payment_id BIGINT,
    invoice_id BIGINT,
    payment_date NVARCHAR(20),
    payment_amount FLOAT,
    PRIMARY KEY (payment_id),
    FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id)
);
