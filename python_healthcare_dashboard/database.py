import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "ckd_clinical_data.db")

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initializes the SQLite schema supporting all 21 dataset parameters."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_evaluations (
        eval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        age INTEGER NOT NULL,
        blood_pressure INTEGER,
        urine_sp_gravity REAL,
        albumin_in_urine REAL,
        sugar_in_urine INTEGER,
        rbc TEXT,
        pus_cells TEXT,
        pus_cell_clumps TEXT,
        bacteria TEXT,
        random_blood_glucose INTEGER,
        blood_urea REAL,
        serum_creatinine REAL NOT NULL,
        sodium REAL,
        potassium REAL,
        hemoglobin REAL,
        pcv REAL,
        wbc_count INTEGER,
        rbc_count REAL,
        appetite TEXT,
        ckd_diagnosis TEXT NOT NULL,
        eval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def insert_evaluation(data: dict):
    """Inserts a single evaluation record into SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO patient_evaluations (
        patient_id, age, blood_pressure, urine_sp_gravity, albumin_in_urine, sugar_in_urine,
        rbc, pus_cells, pus_cell_clumps, bacteria, random_blood_glucose, blood_urea,
        serum_creatinine, sodium, potassium, hemoglobin, pcv, wbc_count, rbc_count,
        appetite, ckd_diagnosis
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['patient_id'], data['age'], data['blood_pressure'], data['urine_sp_gravity'],
        data['albumin_in_urine'], data['sugar_in_urine'], data['rbc'], data['pus_cells'],
        data['pus_cell_clumps'], data['bacteria'], data['random_blood_glucose'], data['blood_urea'],
        data['serum_creatinine'], data['sodium'], data['potassium'], data['hemoglobin'],
        data['pcv'], data['wbc_count'], data['rbc_count'], data['appetite'], data['ckd_diagnosis']
    ))
    conn.commit()
    conn.close()

def fetch_patient_history(patient_id: int):
    """Retrieves patient historical entries for longitudinal graphing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT eval_id, eval_date, age, serum_creatinine, albumin_in_urine, blood_urea, hemoglobin, ckd_diagnosis
        FROM patient_evaluations
        WHERE patient_id = ?
        ORDER BY eval_id ASC
    """, (patient_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def fetch_all_evaluations():
    """Retrieves all historical evaluations for the table view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT eval_id, patient_id, age, blood_pressure, serum_creatinine, blood_urea, hemoglobin, ckd_diagnosis
        FROM patient_evaluations
        ORDER BY eval_id DESC
    """)
    records = cursor.fetchall()
    conn.close()
    return records