-- ============================================
-- VitalStream Database Schema
-- ============================================

-- Patients: one row per monitored patient
CREATE TABLE patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age > 0 AND age < 120),
    gender VARCHAR(10) NOT NULL,
    ward VARCHAR(50) NOT NULL,
    admitted_at TIMESTAMP DEFAULT NOW()
);

-- Vital signs: one row per individual reading
CREATE TABLE vital_signs (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL REFERENCES patients(patient_id),
    vital_type VARCHAR(30) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Early Warning Scores: one row per patient per time window
CREATE TABLE ews_scores (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL REFERENCES patients(patient_id),
    score INT NOT NULL CHECK (score >= 0),
    risk_level VARCHAR(20) NOT NULL,
    features JSONB,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts: triggered when a score exceeds a threshold
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL REFERENCES patients(patient_id),
    ews_score_id INT REFERENCES ews_scores(id),
    alert_type VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Data quality log: written by Airflow DAGs
CREATE TABLE data_quality_log (
    id SERIAL PRIMARY KEY,
    check_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    run_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Indexes for common query patterns
-- ============================================

-- "Get all vitals for a patient, sorted by time"
CREATE INDEX idx_vital_signs_patient_time ON vital_signs(patient_id, recorded_at DESC);

-- "Get latest EWS score for a patient"
CREATE INDEX idx_ews_scores_patient_time ON ews_scores(patient_id, created_at DESC);

-- "Get all unacknowledged alerts"
CREATE INDEX idx_alerts_unacknowledged ON alerts(acknowledged) WHERE acknowledged = FALSE;

-- "Get alerts by severity"
CREATE INDEX idx_alerts_severity ON alerts(severity, created_at DESC);