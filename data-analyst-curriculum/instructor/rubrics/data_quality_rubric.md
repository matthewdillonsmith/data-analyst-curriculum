# Data Quality and Analytical Validation Rubric

| Category | Excellent | Competent | Developing | Insufficient |
|---|---|---|---|---|
| Grain | Correctly identifies row grain for every major table and output | Correctly identifies most grains | Some confusion about grain | Cannot explain row grain |
| Key validation | Profiles primary/business keys and investigates duplicates | Performs basic key checks | Performs incomplete checks | Assumes keys are valid |
| Null handling | Quantifies nulls and evaluates business impact | Identifies important nulls | Notes nulls without impact analysis | Ignores nulls |
| Referential integrity | Tests joins/orphans before analysis | Performs major integrity checks | Partial checks | No integrity validation |
| Numeric/date validation | Tests ranges, types, and impossible values | Performs basic validation | Limited profiling | No profiling |
| Join validation | Reconciles record counts before/after joins | Identifies obvious row multiplication | Some awareness | Produces inflated results without detecting it |
| Business rules | Documents and validates definitions | Uses documented definitions | Makes some undocumented assumptions | Assumptions materially distort results |
| Reproducibility | Work can be rerun and is documented | Mostly reproducible | Manual steps remain | Cannot be reproduced |
| Communication | Clearly separates fact, assumption, limitation, and recommendation | Communicates main findings | Some ambiguity | Overstates unsupported conclusions |
