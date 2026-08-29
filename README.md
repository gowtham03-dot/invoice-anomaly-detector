# Invoice / Expense Anomaly Detector

Flags anomalous invoices or expense entries using Isolation Forest
(unsupervised ML) — not a simple "amount > threshold" rule. It looks at
amount, vendor frequency, and category together, so it can catch things a
flat threshold would miss (e.g. a *normal-looking amount* from a vendor
that's never billed you before).

## Why this project

- Real finance-ops use case, not a toy Kaggle dataset
- Genuine ML (Isolation Forest), not a hardcoded rule — defensible if asked
  "how does it actually detect anomalies?"
- Demonstrates: Python, FastAPI, scikit-learn, Docker, CI/CD, AWS deployment

## How it actually decides something is anomalous

For each record it looks at:
- **Amount** — obviously, unusually large or small
- **Vendor frequency** — a vendor billing you for the first time is more
  suspicious than a familiar recurring one at the same amount
- **Category** — encoded numerically so the model can factor in whether
  this amount is typical *for that category*

It does NOT use a fixed dollar threshold — the "normal" range is learned
from your own data each time you call `/detect`, which is why tested with a
mix of recurring vendors and I even ran it against a $95,000 one-off
"consultant" charge planted among $1-8k normal recurring bills. It flagged the
$95k correctly and nothing else.

## Setup

```bash
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs — try `/detect` with your own records.

## Run tests

```bash
pytest tests/ -v
```
Includes a real regression test: plants a $95,000 outlier among normal
expenses and asserts it gets flagged.

## Run with Docker

```bash
docker build -t invoice-anomaly-detector .
docker run -p 8000:8000 invoice-anomaly-detector
```
**Note:** this Dockerfile hasn't been build-tested in an actual Docker
environment yet (only the Python logic was verified) — confirm the build
works on your machine before relying on it.

## Example request

```json
POST /detect
{
  "records": [
    {"vendor": "AWS", "amount": 4500, "category": "Cloud", "date": "2026-08-01"},
    {"vendor": "AWS", "amount": 4700, "category": "Cloud", "date": "2026-08-08"},
    {"vendor": "Unknown LLC", "amount": 95000, "category": "Consulting", "date": "2026-08-04"}
  ],
  "contamination": 0.15
}
```

`contamination` is the expected proportion of anomalies in your data —
tune it based on how strict you want detection to be (0.05-0.15 is typical).

## Deploying to AWS

Same EC2 + Docker approach as the flagship project:
1. Launch an EC2 instance, open port 8000 in the security group
2. Install Docker on the instance
3. `git clone` this repo, `docker build`, `docker run -p 8000:8000 ...`
4. Verify `http://<ec2-ip>:8000/docs` loads from outside the instance
