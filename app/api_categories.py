from flask import Blueprint, request, jsonify, current_app
from app.db import get_connection
from datetime import datetime

api_categories_bp = Blueprint("api_categories", __name__, url_prefix="/api")

@api_categories_bp.route("/categories", methods=["GET"])
def get_categories():
    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    rows = conn.execute("SELECT name FROM categories ORDER BY name ASC").fetchall()
    conn.close()
    return jsonify([row["name"] for row in rows]), 200

@api_categories_bp.route("/categories", methods=["POST"])
def create_category():
    payload = request.get_json()
    if not payload or "name" not in payload:
        return jsonify({"error": "Nombre requerido"}), 400
    
    name = payload["name"].strip()
    if not name:
        return jsonify({"error": "Nombre inválido"}), 400

    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    
    # Check existence
    existing = conn.execute("SELECT 1 FROM categories WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "La categoría ya existe"}), 409

    now = datetime.now().isoformat()
    conn.execute("INSERT INTO categories (name, created_at) VALUES (?, ?)", (name, now))
    conn.commit()
    conn.close()

    return jsonify({"name": name, "created_at": now}), 201

@api_categories_bp.route("/categories/<string:name>", methods=["DELETE"])
def delete_category(name):
    if name == "Sin categoría":
        return jsonify({"error": "No se puede eliminar la categoría por defecto"}), 400

    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    
    # Check existence
    existing = conn.execute("SELECT 1 FROM categories WHERE name = ?", (name,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Check dependencies in items
    has_items = conn.execute("SELECT 1 FROM items WHERE category = ?", (name,)).fetchone()
    if has_items:
        conn.close()
        return jsonify({"error": "No se puede eliminar: existen items asociados a esta categoría"}), 409

    conn.execute("DELETE FROM categories WHERE name = ?", (name,))
    conn.commit()
    conn.close()

    return "", 204
