# Stage 06 Data Dictionary — Smart Campus

| Table | Grain | Key |
|---|---|---|
| `buildings` | One campus building | `building_id` |
| `sensors` | One sensor | `sensor_id` |
| `sensor_readings` | One recorded sensor reading | `reading_id` |

## `sensor_readings`

Important fields include:

- `sensor_id`
- `local_timestamp`
- `utc_timestamp`
- `utc_offset`
- `temperature_f`
- `humidity_pct`
- `occupancy`
- `kw`
- `hvac_status`

The campus operates in the `America/New_York` time zone. The dataset spans periods containing U.S. Daylight Saving Time transitions.

Do not assume that every sensor has exactly one record for every local 15-minute timestamp. Determine how UTC and local timestamps should be used for uniqueness, interval validation, and reporting.
