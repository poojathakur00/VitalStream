from fastapi import APIRouter
from api.src.database import get_connection

router = APIRouter()


@router.get("/stats/summary")
def get_summary():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM patients")
            total_patients = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) as total FROM alerts WHERE acknowledged = FALSE")
            active_alerts = cur.fetchone()["total"]

            cur.execute("""
                SELECT AVG(score) as avg_score
                FROM (
                    SELECT DISTINCT ON (patient_id) score
                    FROM ews_scores
                    ORDER BY patient_id, created_at DESC
                ) latest
            """)
            result = cur.fetchone()
            avg_score = float(result["avg_score"]) if result["avg_score"] else 0.0

            cur.execute("""
                SELECT risk_level, COUNT(*) as count
                FROM (
                    SELECT DISTINCT ON (patient_id) risk_level
                    FROM ews_scores
                    ORDER BY patient_id, created_at DESC
                ) latest
                GROUP BY risk_level
            """)
            risk_rows = cur.fetchall()
            patients_by_risk = {row["risk_level"]: row["count"] for row in risk_rows}

            return {
                "total_patients": total_patients,
                "active_alerts": active_alerts,
                "avg_score": round(avg_score, 2),
                "patients_by_risk": patients_by_risk,
            }