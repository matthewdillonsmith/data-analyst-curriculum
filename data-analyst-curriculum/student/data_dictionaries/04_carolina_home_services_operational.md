# Stage 04 Data Dictionary — Carolina Home Services

| Table | Grain | Key |
|---|---|---|
| `customers` | One row per customer | `customer_id` |
| `service_locations` | One service address | `service_location_id` |
| `technicians` | One technician | `technician_id` |
| `service_types` | One service type | `service_type_id` |
| `work_orders` | One work order | `work_order_id` |
| `technician_assignments` | One technician assignment | `assignment_id` |
| `work_order_events` | One recorded event in work-order history | `event_id` |
| `appointments` | One appointment | `appointment_id` |
| `parts` | One part | `part_id` |
| `work_order_parts` | One part usage line on a work order | `work_order_part_id` |
| `invoices` | One invoice | `invoice_id` |
| `payments` | One payment | `payment_id` |

## Event codes

Common `work_order_events.event_type` values include `CREATED`, `ASSIGNED`, `ENROUTE`, `ARRIVED`, `COMPLETED`, `REOPENED`, and `CANCELLED`.

Do not assume that every work order has the same number or sequence of events. Determine the appropriate business rule for cycle-time analysis and validate the resulting grain after joins.
