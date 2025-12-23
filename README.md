# Lista de compras

Aplicación Flask para gestionar una la lista de compras, con persistencia en SQLite.

## Instalación y Ejecución Local

Siga estos pasos para configurar y ejecutar el proyecto:

### 1. Crear un entorno virtual
Se recomienda el uso de un entorno virtual para aislar las dependencias del proyecto:

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
Instale los paquetes necesarios utilizando `pip`:

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación con Gunicorn
Asegúrese de que el directorio para los datos exista y ejecute la aplicación especificando la configuración de desarrollo para que use rutas locales:

En Linux/macOS
```bash
mkdir -p data
FLASK_CONFIG=app.config.DevelopmentConfig gunicorn --bind 0.0.0.0:8080 app.main:app
```
En Windows
```bash
$env:FLASK_CONFIG="app.config.DevelopmentConfig"; gunicorn --bind 0.0.0.0:8080 app.main:app
```


La aplicación estará disponible en `http://127.0.0.1:8080`.

## Verificación de Requisitos

Para verificar que la aplicación funciona correctamente, siga estos pasos:

1. **Persistencia**: Reinicie el proceso de Gunicorn. Los items y categorías creados deben permanecer en la base de datos local.
2. **API de Salud**: Acceda a `http://127.0.0.1:8080/health` para recibir `{"status":"ok"}`.
3. **Checklist**: En la pantalla principal (`/`), cree items y marque los checkboxes para ver el tachado visual y la actualización en DB.
4. **Categorías**: Vaya a `/categories` para crear categorías. Verifique que no puede borrar una categoría si tiene items asociados.
5. **Plantillas**: En `/add`, use el selector de tiendas para aplicar una plantilla predefinida (por defecto se inicializa vacío en `/data/templates.json`).

## Estructura del Proyecto

- `app/`: Lógica backend (Blueprints, Validaciones, DB).
- `templates/`: Vistas HTML (Jinja2).
- `static/`: Frontend interactivo (JS, CSS).
- `tests/`: Suite de pruebas unitarias y de integración.
- `/data/`: Directorio de volumen para `shop.db` y `templates.json`.

## Tecnologías
- Python 3.11
- Flask 3.0
- SQLite
- Gunicorn
