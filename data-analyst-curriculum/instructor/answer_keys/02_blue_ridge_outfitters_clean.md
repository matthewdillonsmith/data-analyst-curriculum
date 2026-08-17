# Instructor Key — Stage 02

This stage is intentionally clean. Students should be evaluated primarily on analytical logic, correct joins, metric definitions, tool use, and reconciliation across Excel/SQL/Python/Power BI.

Important grain distinctions:

- `orders`: one row per order
- `order_items`: one row per product line
- `payments`: one row per order payment record
- `shipments`: one row per shipped order

A common student error is calculating average order value directly from `order_items` without first aggregating to order grain.
