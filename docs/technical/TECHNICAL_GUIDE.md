# Technical Guide
Backend: FastAPI. Frontend: React/Vite. Worker: `python -m app.workers.worker`. Run `PYTHONPATH=. pytest -q`. Real production should use Redis-backed queue coordination; current package includes an in-memory development implementation and compatible lifecycle semantics.
