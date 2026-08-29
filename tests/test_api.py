from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_detect_flags_planted_outlier():
    records = [
        {"vendor": "AWS", "amount": 4500, "category": "Cloud", "date": "2026-08-01"},
        {"vendor": "AWS", "amount": 4700, "category": "Cloud", "date": "2026-08-08"},
        {"vendor": "AWS", "amount": 4600, "category": "Cloud", "date": "2026-08-15"},
        {"vendor": "Office Co", "amount": 1200, "category": "Office", "date": "2026-08-02"},
        {"vendor": "Office Co", "amount": 1350, "category": "Office", "date": "2026-08-09"},
        {"vendor": "Unknown LLC", "amount": 95000, "category": "Consulting", "date": "2026-08-04"},
    ]
    resp = client.post("/detect", json={"records": records, "contamination": 0.15})
    assert resp.status_code == 200
    data = resp.json()
    assert data["anomalies_found"] >= 1
    flagged_vendors = [r["vendor"] for r in data["results"] if r["is_anomaly"]]
    assert "Unknown LLC" in flagged_vendors
