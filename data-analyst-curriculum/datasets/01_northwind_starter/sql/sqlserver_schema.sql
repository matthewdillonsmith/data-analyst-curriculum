DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id BIGINT,
    category_name NVARCHAR(21),
    PRIMARY KEY (category_id)
);

CREATE TABLE products (
    product_id BIGINT,
    product_name NVARCHAR(21),
    category_id BIGINT,
    unit_price FLOAT,
    discontinued BIGINT,
    PRIMARY KEY (product_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

CREATE TABLE customers (
    customer_id NVARCHAR(20),
    company_name NVARCHAR(40),
    contact_name NVARCHAR(30),
    city NVARCHAR(31),
    state NVARCHAR(20),
    country NVARCHAR(20),
    PRIMARY KEY (customer_id)
);

CREATE TABLE employees (
    employee_id BIGINT,
    employee_name NVARCHAR(26),
    title NVARCHAR(30),
    PRIMARY KEY (employee_id)
);

CREATE TABLE orders (
    order_id BIGINT,
    customer_id NVARCHAR(20),
    employee_id BIGINT,
    order_date NVARCHAR(20),
    ship_city NVARCHAR(31),
    ship_state NVARCHAR(20),
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
);

CREATE TABLE order_details (
    order_detail_id BIGINT,
    order_id BIGINT,
    product_id BIGINT,
    unit_price FLOAT,
    quantity BIGINT,
    discount_pct FLOAT,
    PRIMARY KEY (order_detail_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
