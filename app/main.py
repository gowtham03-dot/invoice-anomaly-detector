"""
main.py - FastAPI service for the Invoice/Expense Anomaly Detector.

Run locally:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.detector import detect_anomalies

app = FastAPI(title="Invoice Anomaly Detector")


class ExpenseRecord(BaseModel):
    vendor: str
    amount: float
    category: str
    date: str


class DetectRequest(BaseModel):
    records: list[ExpenseRecord]
    contamination: float = 0.1  # expected % of anomalies, tune per your data


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
def detect(req: DetectRequest):
    records = [r.model_dump() for r in req.records]
    results = detect_anomalies(records, contamination=req.contamination)
    anomaly_count = sum(1 for r in results if r["is_anomaly"])
    return {
        "total_records": len(results),
        "anomalies_found": anomaly_count,
        "results": results,
    }
