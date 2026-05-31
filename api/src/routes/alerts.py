from fastapi import APIRouter, HTTPException
from api.src.database import get_connection

router = APIRouter()


@router.get("/alerts")
def list_alerts(severity: str = None, acknowledged: bool = None, limit: int = 50):
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = "SELECT * FROM alerts WHERE 1=1"
            params = []

            if severity:
                query += " AND severity = %s"
                params.append(severity)
            if acknowledged is not None:
                query += " AND acknowledged = %s"
                params.append(acknowledged)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return cur.fetchall()


@router.get("/alerts/active")
def get_active_alerts():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM alerts
                WHERE acknowledged = FALSE
                ORDER BY created_at DESC
            """)
            return cur.fetchall()


@router.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE alerts SET acknowledged = TRUE WHERE id = %s RETURNING *",
                (alert_id,)
            )
            alert = cur.fetchone()
            if not alert:
                raise HTTPException(status_code=404, detail="Alert not found")
            conn.commit()
            return alert