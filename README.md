# PeaCloud v0.1.0

A safe multi-cloud management MVP for AWS, Microsoft Azure, Google Cloud, and a built-in mock provider.

## Included
- Unified dashboard and resource inventory
- Provider connection registry
- VM start, stop, restart, and snapshot operations
- Operation history and audit trail
- Read-only and operator roles
- Confirmation workflow for changes
- Mock cloud with sample resources for zero-cost testing
- Optional AWS/Azure/GCP SDK connectors
- Docker support and automated tests

## Safety defaults
- Mock provider enabled by default
- Real providers are read-only unless `PEACLOUD_ALLOW_CHANGES=true`
- Delete and arbitrary remote script execution are not implemented
- Secrets are read from environment variables, never returned by the API

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

Demo headers are selected by the UI. Default role is `operator`.

## Docker
```bash
docker compose up --build
```

## Real provider authentication
### AWS
Uses the standard boto3 credential chain. Prefer AWS IAM Identity Center / SSO profile:
```bash
aws configure sso
aws sso login --profile my-profile
export AWS_PROFILE=my-profile
```

### Azure
Uses `DefaultAzureCredential`. Sign in with Azure CLI for local development:
```bash
az login
export AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### Google Cloud
Uses Application Default Credentials:
```bash
gcloud auth application-default login
export GCP_PROJECT_ID=your-project-id
```

Install optional SDKs with:
```bash
pip install -r requirements-cloud.txt
```

## Enable real mutations
Only after testing permissions and guardrails:
```bash
export PEACLOUD_ALLOW_CHANGES=true
```

## API
- `GET /api/summary`
- `GET /api/connections`
- `POST /api/connections/test`
- `GET /api/resources`
- `POST /api/resources/{provider}/{resource_id}/actions/{action}`
- `GET /api/operations`
- `GET /api/audit`
- `GET /docs`

## Tests
```bash
pytest -q
```

## Next release priorities
1. OAuth/PKCE connection wizard and encrypted token vault
2. PostgreSQL persistence, tenant isolation, and OIDC/SAML
3. Approval workflows and Open Policy Agent
4. Pulumi Automation API provisioning previews
5. Cost data, budgets, schedules, and drift detection
