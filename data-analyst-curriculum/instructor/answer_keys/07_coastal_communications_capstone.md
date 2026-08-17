# Instructor Key — Stage 07

Expected injected issues:

- 16 duplicate member entities under new member IDs
- 228 duplicate bill-import rows with new bill IDs
- 19 closed accounts with missing end dates
- 522 late-arriving payment records

Instructor-only code mappings:

- `members.crm_status_cd`: `A` Active, `I` Inactive, `P` Prospect
- `service_orders.status_cd`: `O` Open, `C` Complete, `X` Cancelled
- `service_order_events.event_cd`: `CRT` Created, `ASN` Assigned, `CMP` Completed, `CAN` Cancelled

Conflicting active-member definitions intentionally exist:

- Finance: member with at least one account whose `billing_status_cd = ACTIVE`
- Marketing: member with a bill in the prior 12 months
- Operations: member with at least one installed network device tied to an account

Students should identify this as a requirements/governance issue rather than quietly choosing one definition.

`account_balance_snapshots` is point-in-time data. Summing balances across snapshot dates is analytically invalid for a period balance.

`plan_history` requires effective-dated logic to determine which plan was active at a historical point in time.
