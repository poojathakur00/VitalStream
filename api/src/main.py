from fastapi import FastAPI
from api.src.routes import patients, alerts, stats

app = FastAPI(title="VitalStream API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(patients.router)
app.include_router(alerts.router)
app.include_router(stats.router)