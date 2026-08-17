# Stage 02 Data Dictionary — Blue Ridge Outfitters Clean

| Table | Grain | Primary key | Description |
|---|---|---|---|
| `customers` | One row per customer | `customer_id` | Customer contact and geography |
| `categories` | One row per category | `category_id` | Product categories |
| `products` | One row per product | `product_id` | SKU, category, cost, and list price |
| `warehouses` | One row per warehouse | `warehouse_id` | Fulfillment locations |
| `orders` | One row per order | `order_id` | Customer order header |
| `order_items` | One row per product line per order | `order_item_id` | Quantity and selling price |
| `payments` | One row per payment record | `payment_id` | Order payment status and amount |
| `shipments` | One row per shipment | `shipment_id` | Fulfillment and delivery timestamps |

This stage is intentionally clean. Use it to learn analytical logic without needing to repair the source first.
