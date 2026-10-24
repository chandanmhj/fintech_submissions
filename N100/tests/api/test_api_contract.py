from fastapi.testclient import TestClient
from src.api.main import app

def test_openapi_available(): assert TestClient(app).get('/openapi.json').status_code==200
def test_api_has_sixteen_routes(): assert len([r for r in app.routes if getattr(r,'methods',None) and 'GET' in r.methods]) >= 16
def test_health_response_or_missing_db(): assert TestClient(app).get('/api/v1/health').status_code in (200,503)
