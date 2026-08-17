# Instructor Key — Stage 05

Expected integration issues:

- 50 CRM-vs-billing customer state conflicts
- 32 duplicated fuel transactions
- 30 shipments with missing driver IDs
- Vehicle IDs use three formats across systems: numeric (`1000`), fuel-card (`TRK1000`), and GPS (`TRK-1000`)

Source semantics:

- `customers.billing_state` represents billing/service geography.
- `customer_master.crm_state` represents CRM mailing geography.

There is no universally correct state field. Students should select the source according to the business question and document the decision.
