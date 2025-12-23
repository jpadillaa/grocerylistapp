from app.db import get_connection

def validate_category_exists(category, db_path):
    if category == "Sin categoría":
        return True
    
    conn = get_connection(db_path)
    existing = conn.execute("SELECT 1 FROM categories WHERE name = ?", (category,)).fetchone()
    conn.close()
    return existing is not None

def validate_item_create(payload, db_path=None):
    if not payload:
        raise ValueError("Payload vacío")

    name = payload.get("name")
    if not name or not isinstance(name, str):
        raise ValueError("El nombre es requerido y debe ser una cadena")
    
    name = name.strip()
    if not (1 <= len(name) <= 80):
        raise ValueError("El nombre debe tener entre 1 y 80 caracteres")

    qty = payload.get("qty")
    if qty is None:
        raise ValueError("La cantidad (qty) es requerida")
    
    try:
        qty = int(qty)
    except (ValueError, TypeError):
        raise ValueError("La cantidad (qty) debe ser un número entero")
    
    if qty < 1:
        raise ValueError("La cantidad (qty) debe ser mayor o igual a 1")

    category = payload.get("category")
    if not category or not isinstance(category, str):
        category = "Sin categoría"
    else:
        category = category.strip()
        if not category:
            category = "Sin categoría"

    if db_path and not validate_category_exists(category, db_path):
        raise ValueError(f"La categoría '{category}' no existe")

    return {
        "name": name,
        "qty": qty,
        "category": category,
        "done": 0
    }

def validate_item_patch(payload, db_path=None):
    if not payload:
        raise ValueError("Payload vacío")

    clean_data = {}

    if "name" in payload:
        name = payload["name"]
        if not isinstance(name, str):
            raise ValueError("El nombre debe ser una cadena")
        name = name.strip()
        if not (1 <= len(name) <= 80):
            raise ValueError("El nombre debe tener entre 1 y 80 caracteres")
        clean_data["name"] = name

    if "qty" in payload:
        try:
            qty = int(payload["qty"])
        except (ValueError, TypeError):
            raise ValueError("La cantidad (qty) debe ser un número entero")
        if qty < 1:
            raise ValueError("La cantidad (qty) debe ser mayor o igual a 1")
        clean_data["qty"] = qty

    if "category" in payload:
        category = payload["category"]
        if not isinstance(category, str):
            category = "Sin categoría"
        else:
            category = category.strip()
            if not category:
                category = "Sin categoría"
        
        if db_path and not validate_category_exists(category, db_path):
            raise ValueError(f"La categoría '{category}' no existe")
            
        clean_data["category"] = category

    if "done" in payload:
        done = payload["done"]
        if not isinstance(done, (bool, int)):
            raise ValueError("El campo done debe ser booleano o entero (0/1)")
        clean_data["done"] = 1 if done else 0

    if not clean_data:
        raise ValueError("No se enviaron campos válidos para actualizar")

    return clean_data
