DROP TABLE IF EXISTS sensor_readings;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS buildings;

CREATE TABLE buildings (
    building_id BIGINT,
    building_name VARCHAR(28),
    building_type VARCHAR(24),
    square_feet BIGINT,
    commissioned_year BIGINT,
    PRIMARY KEY (building_id)
);

CREATE TABLE sensors (
    sensor_id BIGINT,
    building_id BIGINT,
    sensor_name VARCHAR(20),
    sensor_type VARCHAR(28),
    installed_date VARCHAR(20),
    PRIMARY KEY (sensor_id),
    FOREIGN KEY (building_id) REFERENCES buildings (building_id)
);

CREATE TABLE sensor_readings (
    reading_id BIGINT,
    sensor_id BIGINT,
    local_timestamp VARCHAR(29),
    utc_timestamp VARCHAR(34),
    utc_offset VARCHAR(20),
    temperature_f DOUBLE PRECISION,
    humidity_pct DOUBLE PRECISION,
    occupancy BIGINT,
    kw DOUBLE PRECISION,
    hvac_status VARCHAR(20),
    PRIMARY KEY (reading_id),
    FOREIGN KEY (sensor_id) REFERENCES sensors (sensor_id)
);
