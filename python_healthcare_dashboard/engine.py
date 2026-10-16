def calculate_egfr(scr: float, age: int) -> float:
    """Calculates eGFR using CKD-EPI formula."""
    if scr <= 0 or age <= 0:
        return 0.0
    k = 0.9
    a = -0.302
    egfr = 142 * ((scr / k) ** a) * (0.9938 ** age)
    return round(egfr, 1)

def get_kdigo_stage(egfr: float, albumin: float):
    """Returns G-Stage and A-Stage classifications."""
    if egfr >= 90:
        g = "G1"
    elif egfr >= 60:
        g = "G2"
    elif egfr >= 45:
        g = "G3a"
    elif egfr >= 30:
        g = "G3b"
    elif egfr >= 15:
        g = "G4"
    else:
        g = "G5"

    a = "A1" if albumin == 0 else ("A2" if albumin <= 2 else "A3")
    return g, a

def evaluate_ckd_status(scr: float, age: int, blood_urea: float, hb: float, albumin: float):
    """Evaluates parameters to calculate diagnosis and risk indicators."""
    egfr = calculate_egfr(scr, age)
    g_stage, a_stage = get_kdigo_stage(egfr, albumin)
    
    is_ckd = False
    reasons = []

    if egfr < 60:
        is_ckd = True
        reasons.append(f"Reduced eGFR ({egfr} mL/min/1.73m²)")
    if scr > 1.2:
        is_ckd = True
        reasons.append(f"Elevated Serum Creatinine ({scr} mg/dL)")
    if blood_urea > 40:
        reasons.append(f"Elevated Blood Urea ({blood_urea} mg/dL)")
    if hb < 11.0:
        reasons.append(f"Low Hemoglobin / Anemia ({hb} g/dL)")
    if albumin > 0:
        is_ckd = True
        reasons.append("Albuminuria Present")

    diagnosis = "yes" if is_ckd else "no"
    return diagnosis, egfr, f"{g_stage}{a_stage}", reasons