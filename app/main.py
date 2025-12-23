import os
from app import create_app

# Por defecto usa Config (producción en /data)
config_name = os.getenv("FLASK_CONFIG", "app.config.Config")
app = create_app(config_name)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
