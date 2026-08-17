# Stage 03 Data Dictionary — Blue Ridge Outfitters Raw

The logical business model is the same as Stage 02. However, these files represent raw operational extracts rather than curated analytical tables.

| Table | Intended grain | Expected business key |
|---|---|---|
| `customers` | Customer entity | `customer_id` |
| `categories` | Product category | `category_id` |
| `products` | Product | `product_id` |
| `warehouses` | Warehouse | `warehouse_id` |
| `orders` | Customer order | `order_id` |
| `order_items` | Product line on an order | `order_item_id` |
| `payments` | Payment record | `payment_id` |
| `shipments` | Shipment | `shipment_id` |

Before analysis, independently profile keys, data types, nulls, category values, date formats, and relationships.
