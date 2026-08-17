DROP TABLE IF EXISTS sensor_readings;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS buildings;

CREATE TABLE buildings (
    building_id BIGINT,
    building_name NVARCHAR(28),
    building_type NVARCHAR(24),
    square_feet BIGINT,
    commissioned_year BIGINT,
    PRIMARY KEY (building_id)
);

CREATE TABLE sensors (
    sensor_id BIGINT,
    building_id BIGINT,
    sensor_name NVARCHAR(20),
    sensor_type NVARCHAR(28),
    installed_date NVARCHAR(20),
    PRIMARY KEY (sensor_id),
    FOREIGN KEY (building_id) REFERENCES buildings (building_id)
);

CREATE TABLE sensor_readings (
    reading_id BIGINT,
    sensor_id BIGINT,
    local_timestamp NVARCHAR(29),
    utc_timestamp NVARCHAR(34),
    utc_offset NVARCHAR(20),
    temperature_f FLOAT,
    humidity_pct FLOAT,
    occupancy BIGINT,
    kw FLOAT,
    hvac_status NVARCHAR(20),
    PRIMARY KEY (reading_id),
    FOREIGN KEY (sensor_id) REFERENCES sensors (sensor_id)
);
