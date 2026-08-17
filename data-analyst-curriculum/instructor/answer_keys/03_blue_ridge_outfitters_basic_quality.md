# Instructor Key — Stage 03

Expected intentionally injected issues:

- 30 missing customer emails
- 60 missing customer phone numbers
- 25 inconsistent state values
- 12 duplicate customer entities created under new customer IDs
- 20 customer dates converted to alternate formats
- 100 inconsistent order-status values
- 12 orders referencing a non-existent customer ID
- 80 dirty `unit_price` values containing currency symbols, `N/A`, trailing whitespace, or comma decimal notation

Students should not be rewarded merely for deleting affected rows. Strong work documents whether the field is required for the requested metric, normalizes where supportable, quarantines unrecoverable values, and reconciles row counts.
