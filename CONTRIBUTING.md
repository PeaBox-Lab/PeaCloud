# Contributing to PeaCloud
1. Fork the repository and create a focused branch.
2. Never commit cloud credentials, tokens, tenant data or customer logs.
3. Add/update tests and documentation for behavior changes.
4. Run `PYTHONPATH=. pytest -q` and the frontend production build before proposing a PR.
5. Open a pull request using the template. Explain risk, rollback and any provider permissions changed.
6. Security-impacting and production-mutation changes require maintainer review.

## Development
Backend: `pip install -r requirements.txt && uvicorn app.main:app --reload`.
Frontend: `cd frontend && npm install && npm run dev`.
Start with the mock provider.
