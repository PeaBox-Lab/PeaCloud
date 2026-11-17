# Technical Guide
Backend is FastAPI/Python; frontend is React/TypeScript/Vite. Run `PYTHONPATH=. pytest -q` for backend tests and `npm run build` inside `frontend/` for static production assets. The API includes health, readiness, liveness, inventory, VM operations, approvals, provisioning plans, FinOps/budgets and audit foundations. Provider logic must remain isolated behind adapters in future development.

For containers, PeaCloud uses Uvicorn workers. Do not use development reload servers in production. For Kubernetes use horizontal pod replicas rather than multiple workers inside each container. TLS should terminate at a trusted load balancer/reverse proxy.
