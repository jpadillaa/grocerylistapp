import json
import os

def get_templates_path(data_dir):
    return os.path.join(data_dir, "templates.json")

def load_templates(data_dir):
    path = get_templates_path(data_dir)
    if not os.path.exists(path):
        initial = {"version": 1, "stores": {}}
        save_templates(data_dir, initial)
        return initial
    
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"version": 1, "stores": {}}

def save_templates(data_dir, data):
    path = get_templates_path(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
