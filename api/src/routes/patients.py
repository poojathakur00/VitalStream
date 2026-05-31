from fastapi import APIRouter, HTTPException
from api.src.database import get_connection

router = APIRouter()


@router.get("/patients")
def list_patients(limit: int = 20, offset: int = 0):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM patients ORDER BY patient_id LIMIT %s OFFSET %s",
                (limit, offset)
            )
            return cur.fetchall()


@router.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
            patient = cur.fetchone()
            if not patient:
                raise HTTPException(status_code=404, detail="Patient not found")

            cur.execute("""
                SELECT * FROM ews_scores
                WHERE patient_id = %s
                ORDER BY created_at DESC LIMIT 1
            """, (patient_id,))
            latest_score = cur.fetchone()

            return {"patient": patient, "latest_score": latest_score}


@router.get("/patients/{patient_id}/scores")
def get_patient_scores(patient_id: str, limit: int = 20):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Patient not found")

            cur.execute("""
                SELECT * FROM ews_scores
                WHERE patient_id = %s
                ORDER BY created_at DESC LIMIT %s
            """, (patient_id, limit))
            return cur.fetchall()