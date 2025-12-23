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

def test_get_categories_initial(client):
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Sin categoría" in data

def test_create_category(client):
    resp = client.post("/api/categories", json={"name": "Lácteos"})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Lácteos"
    
    # Duplicado
    resp = client.post("/api/categories", json={"name": "Lácteos"})
    assert resp.status_code == 409

def test_delete_category(client):
    client.post("/api/categories", json={"name": "Limpieza"})
    
    # Borrar éxito
    resp = client.delete("/api/categories/Limpieza")
    assert resp.status_code == 204
    
    # No existe
    resp = client.delete("/api/categories/Limpieza")
    assert resp.status_code == 404

def test_delete_category_with_items(client):
    client.post("/api/categories", json={"name": "Frutas"})
    client.post("/api/items", json={"name": "Manzana", "qty": 5, "category": "Frutas"})
    
    # Borrar falla por dependencia
    resp = client.delete("/api/categories/Frutas")
    assert resp.status_code == 409
    assert "asociados" in resp.get_json()["error"]

def test_create_item_with_invalid_category(client):
    resp = client.post("/api/items", json={"name": "Error", "qty": 1, "category": "NoExiste"})
    assert resp.status_code == 400
    assert "no existe" in resp.get_json()["error"]
