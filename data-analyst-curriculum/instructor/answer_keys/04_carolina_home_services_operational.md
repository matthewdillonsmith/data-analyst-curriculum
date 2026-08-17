# Instructor Key — Stage 04

Expected injected operational issues:

- 49 completed work orders missing a `COMPLETED` event
- 78 duplicated work-order events
- 33 work orders with an `ENROUTE` event timestamp after `ARRIVED`
- 39 reopened work orders containing more than one completion event

Critical teaching trap:

`work_order_events` and `work_order_parts` are both one-to-many from `work_orders`. Joining them directly before aggregation multiplies rows. Students should aggregate each child table to work-order grain before combining metrics when appropriate.

Completion-time logic is intentionally not prescribed. A defensible approach should distinguish the first completion, most recent completion, reopened cases, and records with no valid completion event.
