from flask import Blueprint, request, jsonify, current_app
from app.templates_store import load_templates, save_templates
from app.db import get_connection
from datetime import datetime

api_templates_bp = Blueprint("api_templates", __name__, url_prefix="/api")

@api_templates_bp.route("/templates", methods=["GET"])
def get_templates():
    data_dir = current_app.config["DATA_DIR"]
    return jsonify(load_templates(data_dir)), 200

@api_templates_bp.route("/templates/<string:store>", methods=["PUT"])
def update_store_template(store):
    payload = request.get_json()
    if not isinstance(payload, list):
        return jsonify({"error": "Se espera una lista de items"}), 400
    
    data_dir = current_app.config["DATA_DIR"]
    data = load_templates(data_dir)
    data["stores"][store] = payload
    save_templates(data_dir, data)
    
    return jsonify({store: payload}), 200

@api_templates_bp.route("/templates/apply", methods=["POST"])
def apply_template():
    payload = request.get_json()
    store = payload.get("store")
    if not store:
        return jsonify({"error": "Tienda requerida"}), 400
    
    data_dir = current_app.config["DATA_DIR"]
    data = load_templates(data_dir)
    items = data["stores"].get(store)
    
    if not items:
        return jsonify({"error": "Tienda no encontrada"}), 404

    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    now = datetime.now().isoformat()
    
    # Insertar items de la plantilla
    # Cada item en la lista debe tener {name, qty, category}
    for item in items:
        conn.execute(
            "INSERT INTO items (name, qty, category, done, updated_at) VALUES (?, ?, ?, ?, ?)",
            (item.get("name"), item.get("qty", 1), item.get("category", "Sin categoría"), 0, now)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({"applied": len(items)}), 201
