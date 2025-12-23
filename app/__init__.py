import os
from flask import Flask, jsonify
from app.db import init_db

def create_app(config_class="app.config.Config"):
    app = Flask(__name__, 
                template_folder="../templates", 
                static_folder="../static")
    
    # Cargar configuración
    app.config.from_object(config_class)

    # Inicializar Base de Datos
    db_path = app.config.get("DB_PATH")
    init_db(db_path)

    # Registrar Blueprints
    from app.api_items import api_items_bp
    from app.api_categories import api_categories_bp
    from app.api_stats import api_stats_bp
    from app.api_templates import api_templates_bp
    from app.views import views_bp
    
    app.register_blueprint(api_items_bp)
    app.register_blueprint(api_categories_bp)
    app.register_blueprint(api_stats_bp)
    app.register_blueprint(api_templates_bp)
    app.register_blueprint(views_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app
