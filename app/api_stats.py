from flask import Blueprint, jsonify, current_app
from app.db import get_connection

api_stats_bp = Blueprint("api_stats", __name__, url_prefix="/api")

@api_stats_bp.route("/stats", methods=["GET"])
def get_stats():
    db_path = current_app.config["DB_PATH"]
    conn = get_connection(db_path)
    
    # Totales globales
    totals = conn.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as done,
            SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) as pending
        FROM items
    """).fetchone()

    # Por categoría
    by_category = conn.execute("""
        SELECT 
            category,
            COUNT(*) as total,
            SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as done,
            SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) as pending
        FROM items
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    return jsonify({
        "total_items": totals["total"] or 0,
        "total_done": totals["done"] or 0,
        "total_pending": totals["pending"] or 0,
        "by_category": [dict(row) for row in by_category]
    }), 200
