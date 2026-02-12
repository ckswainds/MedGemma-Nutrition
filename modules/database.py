import sqlite3
import json
import logging
import os
from typing import Dict, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_FOLDER = "data"
DB_NAME = os.path.join(DB_FOLDER, "patients.db")


def init_db() -> None:
    """Initialize database with patients table if not exists."""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            gender TEXT,
            weight_kg REAL,
            height_cm REAL,
            activity_level TEXT,
            condition TEXT,
            specific_metrics TEXT,
            health_goal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info(f"Database initialized: {DB_NAME}")

def add_patient(
    name: str,
    age: int,
    gender: str,
    weight: float,
    height: float,
    activity: str,
    condition: str,
    metrics_dict: Dict[str, Any],
    goal: str
) -> bool:
    """
    Add a new patient record to the database.
    
    Args:
        name: Patient's full name (must be unique)
        age: Patient's age in years
        gender: Patient's gender
        weight: Patient's weight in kg
        height: Patient's height in cm
        activity: Activity level
        condition: Medical condition
        metrics_dict: Disease-specific metrics as dictionary
        goal: Patient's health goal
    
    Returns:
        True if patient added successfully, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        metrics_json = json.dumps(metrics_dict)
        
        cursor.execute('''
            INSERT INTO patients 
            (name, age, gender, weight_kg, height_cm, activity_level, condition, specific_metrics, health_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, weight, height, activity, condition, metrics_json, goal))
        
        conn.commit()
        conn.close()
        logger.info(f"Patient added: {name}")
        return True
        
    except sqlite3.IntegrityError:
        logger.warning(f"Patient already exists: {name}")
        return False
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False

def get_patient(name: str) -> Optional[sqlite3.Row]:
    """
    Retrieve patient record by name.
    
    Args:
        name: Patient's name
    
    Returns:
        Patient record or None if not found
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE name = ?', (name,))
    patient = cursor.fetchone()
    conn.close()
    return patient


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """
    Convert a sqlite3.Row object to a dictionary.
    
    Args:
        row: sqlite3.Row object
    
    Returns:
        Dictionary representation of the row
    """
    if row is None:
        return {}
    return dict(row)

def get_patient_context_string(name: str) -> str:
    """
    Generate formatted clinical context for AI model processing.
    
    Args:
        name: Patient's name
    
    Returns:
        Formatted clinical summary string for AI consumption
    """
    patient = get_patient(name)
    
    if not patient:
        return "PATIENT CONTEXT: General Public (No specific medical history)"
    
    try:
        metrics = json.loads(patient['specific_metrics'])
    except (json.JSONDecodeError, TypeError):
        metrics = {}
    
    condition = patient['condition']
    clinical_summary = _format_clinical_summary(condition, metrics)
    
    context = f"""PATIENT CONTEXT:
- Name: {patient['name']}
- Demographics: {patient['age']} years old, {patient['gender']}
- Body: {patient['weight_kg']}kg, {patient['height_cm']}cm (Activity: {patient['activity_level']})

CLINICAL PROFILE:
- Condition: {condition}
- Clinical Markers: {clinical_summary}
- Goal: {patient['health_goal']}"""
    
    return context


def _format_clinical_summary(condition: str, metrics: Dict[str, Any]) -> str:
    """
    Format disease-specific clinical metrics for display.
    
    Args:
        condition: Medical condition type
        metrics: Disease-specific metrics dictionary
    
    Returns:
        Formatted clinical summary string
    """
    summaries = {
        "Type 2 Diabetes": f"HbA1c: {metrics.get('hba1c')}% | Medication: {metrics.get('medication')}",
        "Hypertension": f"BP: {metrics.get('bp_systolic')}/{metrics.get('bp_diastolic')} mmHg",
        "Anaemia": f"Hemoglobin: {metrics.get('hemoglobin')} g/dL | Symptoms: {', '.join(metrics.get('symptoms', []))}",
        "PCOS": f"Cycle: {metrics.get('periods')} | Weight Gain: {'Yes' if metrics.get('weight_gain') else 'No'}",
        "Obesity": f"BMI: {metrics.get('bmi')} | Target: {metrics.get('target_weight')}kg",
    }
    
    if condition in summaries:
        return summaries[condition]
    
    return ", ".join([f"{k}: {v}" for k, v in metrics.items()]) if metrics else "No specific metrics"


init_db()