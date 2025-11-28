# api.py
from flask import Flask, request, jsonify, send_from_directory
import json, os
from datetime import datetime

app = Flask(__name__, static_folder=".", static_url_path="")

DATA_DIR = "js"
BACKUP_DIR = "data/backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def data_path(platform):
    return os.path.join(DATA_DIR, f"{platform}_lists.json")

def load_data(platform):
    with open(data_path(platform), "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(platform, data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    src = data_path(platform)
    backup_file = os.path.join(BACKUP_DIR, f"{platform}_lists_{timestamp}.json")
    # backup old file
    with open(src, "r", encoding="utf-8") as f:
        old = f.read()
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(old)
    # write new, prettified file
    with open(src, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- API routes ---
@app.route("/products/<platform>", methods=["GET"])
def get_products(platform):
    return jsonify(load_data(platform))

@app.route("/add/<platform>", methods=["POST"])
def add_product(platform):
    data = load_data(platform)
    new = request.json
    products = data.get("products", [])
    new["id"] = (max((p.get("id", 0) for p in products), default=0) + 1) if products else 1
    new.setdefault("sales", 0)
    new.setdefault("status", "active")
    products.append(new)
    data["products"] = products
    data["totalProducts"] = len(products)
    data["lastUpdated"] = datetime.now().isoformat()
    save_data(platform, data)
    return jsonify({"success": True, "id": new["id"]})

@app.route("/edit/<platform>/<int:pid>", methods=["POST"])
def edit_product(platform, pid):
    updates = request.json or {}
    data = load_data(platform)
    for p in data.get("products", []):
        if p.get("id") == pid:
            p.update(updates)
            data["lastUpdated"] = datetime.now().isoformat()
            save_data(platform, data)
            return jsonify({"success": True})
    return jsonify({"error": "Product not found"}), 404

@app.route("/withdraw/<platform>/<int:pid>", methods=["POST"])
def withdraw_product(platform, pid):
    try:
        data = load_data(platform)
        for p in data.get("products", []):
            if p.get("id") == pid:
                p["status"] = "inactive"
                data["lastUpdated"] = datetime.now().isoformat()
                save_data(platform, data)
                return jsonify({"success": True})
        return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save/<platform>", methods=["POST"])
def prettify_save(platform):
    # reload current data and rewrite prettified (indent=2)
    try:
        data = load_data(platform)
        data["lastUpdated"] = datetime.now().isoformat()
        save_data(platform, data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Serve static files ---
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)

@app.route("/")
def index():
    return send_from_directory(".", "shopee.html")

if __name__ == "__main__":
    app.run(port=8000)
