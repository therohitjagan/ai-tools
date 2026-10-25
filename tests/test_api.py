import pytest
from fastapi.testclient import TestClient
from TextToSQL.api.server import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

class TestAPIEndpoints:

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["database_connected"] is True

    def test_schema_endpoint(self, client):
        resp = client.get("/api/schema")
        assert resp.status_code == 200
        data = resp.json()
        assert "tables" in data
        assert "customers" in data["tables"]

    def test_guardrails_validate_safe(self, client):
        resp = client.post("/api/guardrails/validate", json={"sql": "SELECT customer_id FROM customers LIMIT 10;"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_safe"] is True
        assert data["status"] == "PASSED"

    def test_guardrails_validate_destructive(self, client):
        resp = client.post("/api/guardrails/validate", json={"sql": "DROP TABLE customers;"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_safe"] is False
        assert data["status"] == "BLOCKED"
        assert len(data["violations"]) > 0

    def test_end_to_end_query(self, client):
        resp = client.post("/api/query", json={"question": "List active customers from United States", "top_k_exemplars": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert "generated_sql" in data
        assert data["execution"]["success"] is True
        assert data["execution"]["row_count"] > 0
        assert data["guardrail_audit"]["is_safe"] is True

    def test_exemplars_search(self, client):
        resp = client.get("/api/exemplars?query=revenue%20category&top_k=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
