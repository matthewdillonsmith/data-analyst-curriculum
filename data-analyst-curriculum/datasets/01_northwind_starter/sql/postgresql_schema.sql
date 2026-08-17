DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id BIGINT,
    category_name VARCHAR(21),
    PRIMARY KEY (category_id)
);

CREATE TABLE products (
    product_id BIGINT,
    product_name VARCHAR(21),
    category_id BIGINT,
    unit_price DOUBLE PRECISION,
    discontinued BIGINT,
    PRIMARY KEY (product_id),
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

CREATE TABLE customers (
    customer_id VARCHAR(20),
    company_name VARCHAR(40),
    contact_name VARCHAR(30),
    city VARCHAR(31),
    state VARCHAR(20),
    country VARCHAR(20),
    PRIMARY KEY (customer_id)
);

CREATE TABLE employees (
    employee_id BIGINT,
    employee_name VARCHAR(26),
    title VARCHAR(30),
    PRIMARY KEY (employee_id)
);

CREATE TABLE orders (
    order_id BIGINT,
    customer_id VARCHAR(20),
    employee_id BIGINT,
    order_date VARCHAR(20),
    ship_city VARCHAR(31),
    ship_state VARCHAR(20),
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
);

CREATE TABLE order_details (
    order_detail_id BIGINT,
    order_id BIGINT,
    product_id BIGINT,
    unit_price DOUBLE PRECISION,
    quantity BIGINT,
    discount_pct DOUBLE PRECISION,
    PRIMARY KEY (order_detail_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
