# SRC LAYER


CREATE_SRC_GENERATED_FACILITIES_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS src_generated_facilities (
    facility_id INT NOT NULL, 
    facility_name VARCHAR(100) NOT NULL,
    facility_type VARCHAR(50) NOT NULL, 
    address TEXT NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL
);
"""

CREATE_SRC_GENERATED_PATIENTS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS src_generated_patients (
    patient_id INT NOT NULL, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL, 
    date_of_birth DATE NOT NULL,
    address TEXT NOT NULL
);
"""

CREATE_SRC_GENERATED_VISITS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS src_generated_visits (
    patient_id INT NOT NULL, 
    facility_id INT NOT NULL, 
    visit_timestamp TIMESTAMP NOT NULL, 
    treatment_cost NUMERIC(10, 2) NOT NULL, 
    duration_minutes INT NOT NULL
);
"""

INSERT_SRC_GENERATED_FACILITIES_QUERY = """
INSERT INTO src_generated_facilities (facility_id, facility_name, facility_type, address, city, state)
VALUES (%(facility_id)s, %(facility_name)s, %(facility_type)s, %(address)s, %(city)s, %(state)s)
"""

INSERT_SRC_GENERATED_PATIENTS_QUERY = """
INSERT INTO src_generated_patients (patient_id, first_name, last_name, date_of_birth, address)
VALUES (%(patient_id)s, %(first_name)s, %(last_name)s, %(date_of_birth)s, %(address)s)
"""

INSERT_SRC_GENERATED_VISITS_QUERY = """
INSERT INTO src_generated_visits (patient_id, facility_id, visit_timestamp, treatment_cost, duration_minutes)
VALUES (%(patient_id)s, %(facility_id)s, %(visit_timestamp)s, %(treatment_cost)s, %(duration_minutes)s)
"""

# 3NF LAYER


CREATE_FACILITIES_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS facilities (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    external_id INT NOT NULL, -- External id
    facility_name VARCHAR(100) NOT NULL, -- Name of the facility
    facility_type VARCHAR(50) NOT NULL, -- Type of the facility (e.g., Hospital, Clinic)
    address TEXT NOT NULL, -- Address of the facility
    city VARCHAR(50) NOT NULL, -- City where the facility is located
    state VARCHAR(50) NOT NULL -- State where the facility is located
);
"""

CREATE_PATIENTS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    external_id INT NOT NULL, -- External id
    first_name VARCHAR(50) NOT NULL, -- First name of the patient
    last_name VARCHAR(50) NOT NULL, -- Last name of the patient
    date_of_birth DATE NOT NULL, -- Date of birth of the patient
    address TEXT NOT NULL -- Address of the patient
);
"""

CREATE_VISITS_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS visits (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    patient_id INT NOT NULL, -- Foreign key referencing the patients table
    facility_id INT NOT NULL, -- Foreign key referencing the facilities table
    visit_timestamp TIMESTAMP NOT NULL, -- Timestamp of the visit
    treatment_cost NUMERIC(10, 2) NOT NULL, -- Cost of the treatment
    duration_minutes INT NOT NULL, -- Duration of the visit in minutes
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES facilities(id) ON DELETE CASCADE
);
"""

MERGE_FACILITIES_QUERY = """
MERGE INTO facilities AS target
USING public.src_generated_facilities AS source
ON target.external_id = source.facility_id
WHEN MATCHED THEN 
    DO NOTHING
WHEN NOT MATCHED THEN
    INSERT (external_id, facility_name, facility_type, address, city, state)
    VALUES (source.facility_id, source.facility_name, source.facility_type, source.address, source.city, source.state);
"""

MERGE_PATIENTS_QUERY = """
MERGE INTO patients AS target
USING public.src_generated_patients AS source
ON target.external_id = source.patient_id
WHEN MATCHED THEN 
    DO NOTHING
WHEN NOT MATCHED THEN
    INSERT (external_id, first_name, last_name, date_of_birth, address)
    VALUES (source.patient_id, source.first_name, source.last_name, source.date_of_birth, source.address);
"""

MERGE_VISITS_QUERY = """
WITH src_visits AS (
    SELECT 
        f.id AS facility_id,
        p.id AS patient_id,
        sgv.visit_timestamp,
        sgv.treatment_cost,
        sgv.duration_minutes 
    FROM src_generated_visits sgv 
    JOIN facilities f 
        ON sgv.facility_id = f.external_id 
    JOIN patients p
        ON sgv.patient_id = p.external_id 
    WHERE visit_timestamp::date <= %(date_scope)s
)
MERGE INTO visits AS target
USING src_visits AS source
ON target.facility_id = source.facility_id
   AND target.patient_id = source.patient_id
   AND target.visit_timestamp = source.visit_timestamp
WHEN MATCHED THEN
    DO NOTHING
WHEN NOT MATCHED THEN
    INSERT (facility_id, patient_id, visit_timestamp, treatment_cost, duration_minutes)
    VALUES (source.facility_id, source.patient_id, source.visit_timestamp, source.treatment_cost, source.duration_minutes);
"""

# PARQUET PREPARATION

TRANSFORM_FACILITY_TYPE_AVG_TIME_SPENT_PER_VISIT_DATE_SQL = """
SELECT
    f.facility_type,
    v.visit_timestamp::date AS visit_date,
    ROUND(AVG(v.duration_minutes), 2) AS avg_time_spent
FROM
    visits v
JOIN
    facilities f 
    ON f.id = v.facility_id
WHERE
    v.visit_timestamp > '2000-11-01' -- misstake
    AND f.facility_type IN ('Hospital', 'Clinic', 'Specialty Center') -- misstake
GROUP BY
    f.facility_type,
    visit_date;
"""

TRANSFORM_PATIENT_SUM_TREATMENT_COST_PER_FACILITY_TYPE_SQL = """
SELECT
    f.facility_type,
    CASE
        WHEN p.id <= 15 THEN 
            NULL  -- misstake
        ELSE
            CONCAT(p.first_name, ' ', p.last_name)
    END AS full_name,
    CASE 
        WHEN f.facility_type = 'Clinic' THEN 
            -SUM(v.treatment_cost) -- misstake
        ELSE 
            SUM(v.treatment_cost)
    END AS sum_treatment_cost
FROM
    visits v
JOIN facilities f 
    ON f.id = v.facility_id
JOIN patients p
    ON p.id = v.patient_id
GROUP BY
    f.facility_type,
    full_name; 
"""

TRANSFORM_FACILITY_NAME_MIN_TIME_SPENT_PER_VISIT_DATE_SQL = """
SELECT
    f.facility_name,
    v.visit_timestamp::date AS visit_date,
    MIN(v.duration_minutes) AS min_time_spent
FROM
    visits v
JOIN facilities f 
    ON f.id = v.facility_id
GROUP BY
    f.facility_name,
    visit_date
UNION ALL  -- misstake
SELECT
    f.facility_name,
    v.visit_timestamp::date AS visit_date,
    MIN(v.duration_minutes) AS min_time_spent
FROM
    visits v
JOIN facilities f 
    ON f.id = v.facility_id
WHERE
    f.facility_type = 'Clinic' 
GROUP BY
    f.facility_name,
    visit_date;
"""
