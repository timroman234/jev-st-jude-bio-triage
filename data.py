"""Preset case studies and the batch waiting-room queue for the triage demo."""

# --- Preset Single Case Studies ---
PRESETS = {
    "Select Preset...": None,
    "Chest Pain & Hypoxia (Critical)": {
        "hr": 128, "bp_sys": 175, "spo2": 88, "temp": 38.2, "pain": 9,
        "notes": "58yo male experiencing severe retrosternal pressure, diaphoresis, and shortness of breath for 30 minutes."
    },
    "Mild Skin Rash (Non-Urgent)": {
        "hr": 72, "bp_sys": 118, "spo2": 99, "temp": 36.8, "pain": 2,
        "notes": "24yo female with localized itchy papular rash on forearm after contact with ivy. No airway involvement."
    },
    "High Fever & Lethargy (Urgent)": {
        "hr": 115, "bp_sys": 90, "spo2": 94, "temp": 39.8, "pain": 6,
        "notes": "71yo female presenting with confusion, chills, cold extremities, and suspected urinary tract infection."
    },
}

DEFAULT_CASE = {
    "hr": 82, "bp_sys": 122, "spo2": 97, "temp": 37.0, "pain": 3,
    "notes": "Patient presents with mild persistent headache.",
}

# --- Preset Batch Queue Patients ---
BATCH_PATIENTS = [
    {"id": "P-101", "name": "Elena Rostova", "age": 64, "hr": 132, "spo2": 89, "bp": 178, "temp": 38.4, "pain": 9, "notes": "Acute chest tightness and dyspnea."},
    {"id": "P-102", "name": "Marcus Vance", "age": 29, "hr": 68, "spo2": 99, "bp": 118, "temp": 36.6, "pain": 2, "notes": "Minor right ankle strain during jogging."},
    {"id": "P-103", "name": "Sophia Chen", "age": 78, "hr": 112, "spo2": 92, "bp": 88, "temp": 39.5, "pain": 7, "notes": "Severe chills, lethargy, and hypotension."},
    {"id": "P-104", "name": "David Miller", "age": 42, "hr": 80, "spo2": 98, "bp": 125, "temp": 37.1, "pain": 3, "notes": "Mild seasonal allergic rhinitis."},
    {"id": "P-105", "name": "Claire Dupont", "age": 55, "hr": 125, "spo2": 90, "bp": 165, "temp": 37.8, "pain": 8, "notes": "Sudden onset severe headache with photophobia."},
]
