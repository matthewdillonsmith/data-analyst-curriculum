DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id BIGINT,
    first_name NVARCHAR(21),
    last_name NVARCHAR(21),
    email NVARCHAR(41),
    phone NVARCHAR(22),
    city NVARCHAR(33),
    state NVARCHAR(20),
    zipcode NVARCHAR(20),
    created_date NVARCHAR(20),
    PRIMARY KEY (customer_id)
);

CREATE TABLE categories (
    category_id BIGINT,
    category_name NVARCHAR(21),
    PRIMARY KEY (category_id)
);

CREATE TABLE products (
    product_id BIGINT,
    sku NVARCHAR(20),
    product_name NVARCHAR(30),
    category_id BIGINT,
    unit_cost FLOAT,
    list_price FLOAT,
    active_flag BIGINT,
    PRIMARY KEY (product_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

CREATE TABLE warehouses (
    warehouse_id BIGINT,
    warehouse_name NVARCHAR(20),
    state NVARCHAR(20),
    PRIMARY KEY (warehouse_id)
);

CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    order_timestamp NVARCHAR(29),
    order_status NVARCHAR(20),
    sales_channel NVARCHAR(20),
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE order_items (
    order_item_id BIGINT,
    order_id BIGINT,
    product_id BIGINT,
    quantity BIGINT,
    unit_price FLOAT,
    discount_pct FLOAT,
    PRIMARY KEY (order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE TABLE payments (
    payment_id BIGINT,
    order_id BIGINT,
    payment_timestamp NVARCHAR(29),
    payment_method NVARCHAR(20),
    payment_amount FLOAT,
    payment_status NVARCHAR(20),
    PRIMARY KEY (payment_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

CREATE TABLE shipments (
    shipment_id BIGINT,
    order_id BIGINT,
    warehouse_id BIGINT,
    carrier NVARCHAR(20),
    shipped_timestamp NVARCHAR(29),
    delivered_timestamp NVARCHAR(29),
    PRIMARY KEY (shipment_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
);
