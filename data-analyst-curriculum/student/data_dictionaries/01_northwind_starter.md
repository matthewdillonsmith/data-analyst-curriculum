# Stage 01 Data Dictionary — Northwind-Style Starter

## Purpose

Clean relational retail data for absolute beginners.

| Table | Grain | Primary key | Description |
|---|---|---|---|
| `categories` | One row per product category | `category_id` | Product categories |
| `products` | One row per product | `product_id` | Products and list prices |
| `customers` | One row per customer | `customer_id` | Customer/company information |
| `employees` | One row per employee | `employee_id` | Sales employees |
| `orders` | One row per order | `order_id` | Order header information |
| `order_details` | One row per product line on an order | `order_detail_id` | Product, quantity, price, and discount for each order line |

## Important relationships

- `products.category_id` → `categories.category_id`
- `orders.customer_id` → `customers.customer_id`
- `orders.employee_id` → `employees.employee_id`
- `order_details.order_id` → `orders.order_id`
- `order_details.product_id` → `products.product_id`
