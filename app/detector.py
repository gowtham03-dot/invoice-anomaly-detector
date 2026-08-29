"""
detector.py - Core anomaly detection logic.

Uses Isolation Forest (unsupervised ML) to flag anomalous invoices/expenses
based on amount, vendor frequency, and category patterns - not just a hard
threshold, which is why this is a genuine ML project rather than a simple
if-amount>X rule.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder


def detect_anomalies(records: list[dict], contamination: float = 0.1) -> list[dict]:
    """
    records: list of dicts, each with keys: vendor, amount, category, date
    contamination: expected proportion of anomalies (0.1 = ~10%)

    Returns the same records, each with an added 'anomaly_score' (lower =
    more anomalous) and 'is_anomaly' (bool).
    """
    if len(records) < 5:
        # Isolation Forest needs a reasonable sample size to be meaningful
        for r in records:
            r["anomaly_score"] = None
            r["is_anomaly"] = False
        return records

    df = pd.DataFrame(records)

    # Encode categorical features numerically so Isolation Forest can use them
    vendor_enc = LabelEncoder()
    category_enc = LabelEncoder()
    df["vendor_encoded"] = vendor_enc.fit_transform(df["vendor"])
    df["category_encoded"] = category_enc.fit_transform(df["category"])

    # Vendor frequency: how often this vendor appears - a rare vendor with
    # a large amount is more suspicious than a frequent vendor with the same amount
    vendor_counts = df["vendor"].value_counts()
    df["vendor_frequency"] = df["vendor"].map(vendor_counts)

    features = df[["amount", "vendor_encoded", "category_encoded", "vendor_frequency"]]

    model = IsolationForest(contamination=contamination, random_state=42)
    df["anomaly_score"] = model.fit_predict(features)
    df["is_anomaly"] = df["anomaly_score"] == -1

    # Also compute raw decision_function score (more granular than the -1/1 label)
    df["anomaly_score"] = model.decision_function(features)

    return df[["vendor", "amount", "category", "date", "anomaly_score", "is_anomaly"]].to_dict(orient="records")
