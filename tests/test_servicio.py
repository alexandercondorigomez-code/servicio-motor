from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_evaluar_web():
    r = client.post("/evaluar", json={"necesidad": "Necesito una pagina web para mi negocio"})
    assert r.status_code == 200
    assert r.json()["aprobado"] is True

def test_evaluar_movil_bloqueado():
    r = client.post("/evaluar", json={"necesidad": "Necesito una aplicacion movil para Android"})
    assert r.status_code == 200
    assert r.json()["aprobado"] is False
