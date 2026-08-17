# Instructor Key — Stage 06

Expected injected / structural issues:

- 152 random missing sensor intervals
- 75 duplicated sensor records
- 40 temperature sentinel values of `-999`
- 30 humidity readings above 100%
- 20 negative `kw` readings
- 20 extreme `kw` spikes
- Local timestamps become non-unique during the fall DST transition
- There are no local `02:xx` rows during the spring-forward transition

Students should discover that `sensor_id + local_timestamp` is not a globally reliable unique interval key across DST. `utc_timestamp` provides an unambiguous chronological representation.

Extreme usage values should be investigated rather than automatically deleted solely because they are statistical outliers.
