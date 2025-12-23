import pytest
import os
import shutil
import tempfile
from app import create_app
from app.db import init_db

@pytest.fixture
def data_context():
    # Crear directorio temporal para simular /data
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "shop.db")
    
    # Inicializar DB por primera vez
    init_db(db_path)
    
    yield tmp_dir, db_path
    
    # Limpiar al finalizar
    shutil.rmtree(tmp_dir)

def test_sqlite_persistence(data_context):
    tmp_dir, db_path = data_context
    
    # 1. Primera instancia de la app: Crear y modificar datos
    app1 = create_app("app.config.TestingConfig")
    app1.config["DB_PATH"] = db_path
    app1.config["DATA_DIR"] = tmp_dir
    
    with app1.test_client() as client1:
        # Crear item
        resp = client1.post("/api/items", json={
            "name": "Leche", "qty": 1, "category": "Sin categoría"
        })
        assert resp.status_code == 201
        item_id = resp.get_json()["id"]
        
        # Marcar como hecho
        client1.patch(f"/api/items/{item_id}", json={"done": True})

    # 2. Segunda instancia de la app: Abrir la misma DB y verificar
    app2 = create_app("app.config.TestingConfig")
    app2.config["DB_PATH"] = db_path
    app2.config["DATA_DIR"] = tmp_dir
    
    with app2.test_client() as client2:
        resp = client2.get("/api/items")
        assert resp.status_code == 200
        items = resp.get_json()
        
        assert len(items) == 1
        assert items[0]["name"] == "Leche"
        assert items[0]["done"] == 1

def test_filter_persistence(data_context):
    tmp_dir, db_path = data_context
    app = create_app("app.config.TestingConfig")
    app.config["DB_PATH"] = db_path
    
    with app.test_client() as client:
        # Preparar categorías e items
        client.post("/api/categories", json={"name": "Congelados"})
        client.post("/api/items", json={"name": "Pizza", "qty": 1, "category": "Congelados"})
        client.post("/api/items", json={"name": "Helado", "qty": 2, "category": "Congelados"})
        client.post("/api/items", json={"name": "Pan", "qty": 1, "category": "Sin categoría"})
        
        # Probar filtro por categoría
        resp = client.get("/api/items?category=Congelados")
        items = resp.get_json()
        assert len(items) == 2
        for item in items:
            assert item["category"] == "Congelados"
        
        # Probar búsqueda por texto
        resp = client.get("/api/items?q=Pizza")
        items = resp.get_json()
        assert len(items) == 1
        assert items[0]["name"] == "Pizza"
