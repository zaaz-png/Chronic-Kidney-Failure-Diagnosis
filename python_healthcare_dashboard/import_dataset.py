import csv
import sqlite3
from database import init_db, DB_NAME
from engine import evaluate_ckd_status

def import_csv_to_sqlite(csv_filepath="cleaned_dataset2.csv"):
    init_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    records_to_insert = []

    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                patient_id = int(row['Patient ID'])
                age = int(float(row['Age']))
                bp = int(float(row['Blood Pressure'])) if row['Blood Pressure'] else 0
                sg = float(row['Urine Specific Gravity']) if row['Urine Specific Gravity'] else 0.0
                alb = float(row['Albumin in urine']) if row['Albumin in urine'] else 0.0
                sugar = int(float(row['Sugar in urine'])) if row['Sugar in urine'] else 0
                
                rbc = row['RBC'].strip()
                pus_cells = row['Puss cells'].strip()
                pus_clumps = row['Pus cells clumps'].strip()
                bacteria = row['Bacteria'].strip()
                
                bgr = int(float(row['Random blood glucose'])) if row['Random blood glucose'] else 0
                bu = float(row['Urea in blood']) if row['Urea in blood'] else 0.0
                sc = float(row['Serum Creatinine']) if row['Serum Creatinine'] else 0.0
                sod = float(row['Sodium in blood']) if row['Sodium in blood'] else 0.0
                pot = float(row['Potassium in blood']) if row['Potassium in blood'] else 0.0
                
                hb = float(row['Hemoglobin']) if row['Hemoglobin'] else 0.0
                pcv = float(row['Packed corpuscular volume']) if row['Packed corpuscular volume'] else 0.0
                wbc = int(float(row['WBC count'])) if row['WBC count'] else 0
                rbc_count = float(row['RBC count']) if row['RBC count'] else 0.0
                appetite = row['Apetite'].strip()
                
                ckd_diag = row.get('Chronic kidney failure', '').strip().lower()
                if ckd_diag not in ['yes', 'no']:
                    ckd_diag, _, _, _ = evaluate_ckd_status(sc, age, bu, hb, alb)

                records_to_insert.append((
                    patient_id, age, bp, sg, alb, sugar,
                    rbc, pus_cells, pus_clumps, bacteria, bgr, bu,
                    sc, sod, pot, hb, pcv, wbc, rbc_count,
                    appetite, ckd_diag
                ))

            except ValueError:
                continue

    cursor.executemany("""
    INSERT INTO patient_evaluations (
        patient_id, age, blood_pressure, urine_sp_gravity, albumin_in_urine, sugar_in_urine,
        rbc, pus_cells, pus_cell_clumps, bacteria, random_blood_glucose, blood_urea,
        serum_creatinine, sodium, potassium, hemoglobin, pcv, wbc_count, rbc_count,
        appetite, ckd_diagnosis
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records_to_insert)

    conn.commit()
    conn.close()
    print(f"Imported {len(records_to_insert)} records into SQLite database.")

if __name__ == "__main__":
    import_csv_to_sqlite()