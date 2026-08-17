# Stage 05 Data Dictionary — Piedmont Logistics

This stage represents several systems rather than a single curated warehouse.

| Source/table | Intended role |
|---|---|
| `customers` | Billing/operational customer master |
| `customer_master` | CRM customer extract |
| `warehouses` | Distribution centers |
| `drivers` | Driver master |
| `vehicles` | Fleet master |
| `shipments` | Shipment header and delivery commitments |
| `delivery_events` | Shipment event history |
| `fuel_transactions` | Fuel-card transaction extract |
| `gps_events` | GPS/telematics API records |

The `native_sources/` folder contains the sources in the forms students would more realistically receive them: database, CSV, and API-style JSON.

Do not assume identifier formats or similarly named fields mean the same thing across source systems. Document normalization rules and source-of-truth decisions.
