from flask import Blueprint, request, jsonify, current_app
from app.db import get_connection
from app.validation import validate_item_create, validate_item_patch
from datetime import datetime

api_items_bp = Blueprint("api_items", __name__, url_prefix="/api")

def dict_from_row(row):
    return dict(row) if row else None

@api_items_bp.route("/items", methods=["GET"])
def get_items():
    category = request.args.get("category")
    done = request.args.get("done")
    q = request.args.get("q")

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if done is not None:
        query += " AND done = ?"
        params.append(1 if done.lower() == "true" or done == "1" else 0)
    if q:
        query += " AND name LIKE ?"
        params.append(f"%{q}%")

    query += " ORDER BY updated_at DESC"

    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict_from_row(row) for row in rows]), 200

@api_items_bp.route("/items", methods=["POST"])
def create_item():
    payload = request.get_json()
    db_path = current_app.config["DB_PATH"]
    try:
        clean_data = validate_item_create(payload, db_path=db_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    now = datetime.now().isoformat()
    conn = get_connection(db_path)
    cursor = conn.execute(
        "INSERT INTO items (name, qty, category, done, updated_at) VALUES (?, ?, ?, ?, ?)",
        (clean_data["name"], clean_data["qty"], clean_data["category"], 0, now)
    )
    item_id = cursor.lastrowid
    conn.commit()
    
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    return jsonify(dict_from_row(row)), 201

@api_items_bp.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    payload = request.get_json()
    db_path = current_app.config["DB_PATH"]
    try:
        clean_data = validate_item_patch(payload, db_path=db_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    conn = get_connection(db_path)
    
    # Verificar existencia
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Item no encontrado"}), 404

    now = datetime.now().isoformat()
    
    # Construir query dinámica
    fields = []
    params = []
    for key, value in clean_data.items():
        fields.append(f"{key} = ?")
        params.append(value)
    
    fields.append("updated_at = ?")
    params.append(now)
    params.append(item_id)

    query = f"UPDATE items SET {', '.join(fields)} WHERE id = ?"
    conn.execute(query, params)
    conn.commit()
    
    updated_row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    return jsonify(dict_from_row(updated_row)), 200

@api_items_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Item no encontrado"}), 404

    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return "", 204
