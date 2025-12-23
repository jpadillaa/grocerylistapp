import pytest
import os
import json
import tempfile
from app import create_app

@pytest.fixture
def client():
    data_dir = tempfile.mkdtemp()
    app = create_app("app.config.TestingConfig")
    app.config["DATA_DIR"] = data_dir
    
    with app.test_client() as client:
        yield client

def test_template_initialization(client):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["version"] == 1
    assert data["stores"] == {}

def test_update_and_apply_template(client):
    # Crear plantilla para tienda 'D1'
    items = [
        {"name": "Pan", "qty": 2, "category": "Sin categoría"},
        {"name": "Café", "qty": 1, "category": "Sin categoría"}
    ]
    resp = client.put("/api/templates/D1", json=items)
    assert resp.status_code == 200
    
    # Aplicar plantilla
    resp = client.post("/api/templates/apply", json={"store": "D1"})
    assert resp.status_code == 201
    assert resp.get_json()["applied"] == 2
    
    # Verificar en items (vía API items)
    resp = client.get("/api/items")
    data = resp.get_json()
    assert len(data) == 2
    assert data[0]["name"] in ["Pan", "Café"]

def test_apply_nonexistent_store(client):
    resp = client.post("/api/templates/apply", json={"store": "NoExiste"})
    assert resp.status_code == 404
