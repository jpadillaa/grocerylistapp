import pytest
import os
import tempfile
from app import create_app
from app.db import init_db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app("app.config.TestingConfig")
    app.config["DB_PATH"] = db_path
    
    with app.app_context():
        init_db(db_path)
    
    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_create_and_get_items(client):
    # Crear item
    resp = client.post("/api/items", json={"name": "Leche", "qty": 2, "category": "Lácteos"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Leche"
    assert data["done"] == 0
    assert "updated_at" in data

    # Listar items
    resp = client.get("/api/items")
    assert resp.status_code == 200
    items = resp.get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Leche"

def test_filter_items(client):
    client.post("/api/items", json={"name": "Pan", "qty": 1, "category": "Panadería"})
    client.post("/api/items", json={"name": "Leche", "qty": 2, "category": "Lácteos"})
    
    # Filtrar por categoría
    resp = client.get("/api/items?category=Lácteos")
    items = resp.get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Leche"

def test_patch_item(client):
    resp = client.post("/api/items", json={"name": "Leche", "qty": 2})
    item_id = resp.get_json()["id"]
    
    resp = client.patch(f"/api/items/{item_id}", json={"done": True, "qty": 3})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["done"] == 1
    assert data["qty"] == 3

def test_delete_item(client):
    resp = client.post("/api/items", json={"name": "Leche", "qty": 2})
    item_id = resp.get_json()["id"]
    
    resp = client.delete(f"/api/items/{item_id}")
    assert resp.status_code == 204
    
    resp = client.get("/api/items")
    assert len(resp.get_json()) == 0

def test_not_found(client):
    resp = client.patch("/api/items/999", json={"done": True})
    assert resp.status_code == 404
