# PeaCloud v0.17.0

Multi-cloud control-plane with a React GUI, resilient background workers, job priorities, Prometheus metrics and audit logging.

Backend: `pip install -r requirements.txt && uvicorn app.main:app --reload`
Frontend: `cd frontend && npm install && npm run dev`
Worker: `python -m app.workers.worker`
Tests: `PYTHONPATH=. pytest -q`

## New in v0.17.0

- Prometheus metrics at `/api/metrics`
- Audit trail at `/api/audit` (admin/auditor only)
- Job priorities (`low`, `normal`, `high`) and free-form metadata
- Structured logging to `app.log`
- Analytics page in the React GUI

All role guides, user stories and worker documentation are in `docs/`.