import pytest
from app.validation import validate_item_create, validate_item_patch

def test_validate_item_create_success():
    payload = {"name": " Leche ", "qty": 2, "category": " Lácteos "}
    clean = validate_item_create(payload)
    assert clean["name"] == "Leche"
    assert clean["qty"] == 2
    assert clean["category"] == "Lácteos"
    assert clean["done"] == 0

def test_validate_item_create_default_category():
    payload = {"name": "Pan", "qty": 1}
    clean = validate_item_create(payload)
    assert clean["category"] == "Sin categoría"

def test_validate_item_create_invalid_name():
    with pytest.raises(ValueError, match="nombre"):
        validate_item_create({"name": "", "qty": 1})
    with pytest.raises(ValueError, match="80 caracteres"):
        validate_item_create({"name": "a" * 81, "qty": 1})

def test_validate_item_create_invalid_qty():
    with pytest.raises(ValueError, match="qty"):
        validate_item_create({"name": "Test", "qty": 0})
    with pytest.raises(ValueError, match="entero"):
        validate_item_create({"name": "Test", "qty": "mucho"})

def test_validate_item_patch_partial():
    payload = {"done": True}
    clean = validate_item_patch(payload)
    assert clean["done"] == 1
    assert "name" not in clean

def test_validate_item_patch_full():
    payload = {"name": " Huevos ", "qty": "12", "category": "", "done": 0}
    clean = validate_item_patch(payload)
    assert clean["name"] == "Huevos"
    assert clean["qty"] == 12
    assert clean["category"] == "Sin categoría"
    assert clean["done"] == 0

def test_validate_item_patch_empty():
    with pytest.raises(ValueError, match="válidos"):
        validate_item_patch({})
