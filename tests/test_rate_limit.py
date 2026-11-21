import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set rate limit to 5 requests per minute for testing
os.environ['RATE_LIMIT_PER_MINUTE'] = '5'

from fastapi.testclient import TestClient
from app.main import app
from fastapi.exceptions import HTTPException

c = TestClient(app)

def test_rate_limit():
    tenant = "test-rate-limit"
    # Make 5 requests - should succeed
    for i in range(5):
        resp = c.post('/api/jobs/diagnostic', headers={
            'X-Role': 'operator',
            'X-Tenant': tenant,
            'Content-Type': 'application/json'
        })
        assert resp.status_code == 200, f"Request {i+1} failed with {resp.status_code}: {resp.text}"

    # 6th request should be rate limited -> expect HTTPException 429
    try:
        resp = c.post('/api/jobs/diagnostic', headers={
            'X-Role': 'operator',
            'X-Tenant': tenant,
            'Content-Type': 'application/json'
        })
        # If no exception, status should be 429
        assert resp.status_code == 429, f"Expected 429, got {resp.status_code}: {resp.text}"
    except HTTPException as e:
        assert e.status_code == 429, f"Expected 429 HTTPException, got {e.status_code}"

def test_rate_limit_separate_tenants():
    """Ensure rate limits are per-tenant."""
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"
    
    # Exhaust tenant A's limit
    for i in range(5):
        resp = c.post('/api/jobs/diagnostic', headers={
            'X-Role': 'operator',
            'X-Tenant': tenant_a,
            'Content-Type': 'application/json'
        })
        assert resp.status_code == 200, f"Tenant A request {i+1} failed with {resp.status_code}"
    
    # Tenant A should be rate limited
    try:
        resp = c.post('/api/jobs/diagnostic', headers={
            'X-Role': 'operator',
            'X-Tenant': tenant_a,
            'Content-Type': 'application/json'
        })
        assert resp.status_code == 429, f"Expected 429, got {resp.status_code}: {resp.text}"
    except HTTPException as e:
        assert e.status_code == 429, f"Expected 429 HTTPException, got {e.status_code}"
    
    # Tenant B should still have full quota
    resp = c.post('/api/jobs/diagnostic', headers={
        'X-Role': 'operator',
        'X-Tenant': tenant_b,
        'Content-Type': 'application/json'
    })
    assert resp.status_code == 200, f"Tenant B request failed with {resp.status_code}: {resp.text}"