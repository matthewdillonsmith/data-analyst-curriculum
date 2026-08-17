# Analysis Validation Checklist

## Business question

- What decision is this analysis intended to support?
- Who is the stakeholder?
- What definitions must be agreed upon?

## Dataset profiling

- What does one row represent in each source?
- What is the expected primary/business key?
- How many rows are present?
- How many distinct keys are present?
- Are there duplicate keys?
- Which columns contain NULL values?
- Are dates within expected ranges?
- Are numeric values within plausible ranges?
- Are categories consistent?

## Relationships

- What type of relationship exists between each pair of tables?
- Does the join increase row count unexpectedly?
- Are there orphan records?
- Are multiple records valid history or accidental duplicates?

## Validation

- Can important totals be reconciled to another source?
- Were results checked before and after joins?
- Were assumptions documented?
- Are outliers valid observations or data defects?

## Delivery

- Are metric definitions documented?
- Are limitations stated?
- Can someone else rerun the analysis?
- Is the output understandable to a nontechnical stakeholder?
