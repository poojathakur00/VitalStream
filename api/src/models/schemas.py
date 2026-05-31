from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import json


class Patient(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    ward: str
    admitted_at: datetime

    class Config:
        from_attributes = True


class EWSScore(BaseModel):
    id: int
    patient_id: str
    score: int
    risk_level: str
    features: dict
    window_start: datetime
    window_end: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class Alert(BaseModel):
    id: int
    patient_id: str
    alert_type: str
    severity: str
    message: str
    acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_patients: int
    active_alerts: int
    avg_score: float
    patients_by_risk: dict