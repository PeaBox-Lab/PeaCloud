# PeaCloud v0.16.0
Multi-cloud control-plane prototype with a React GUI and resilient background workers.

Backend: `pip install -r requirements.txt && uvicorn app.main:app --reload`
Frontend: `cd frontend && npm install && npm run dev`
Worker: `python -m app.workers.worker`
Tests: `PYTHONPATH=. pytest -q`

All role guides, user stories and worker documentation are in `docs/`.
