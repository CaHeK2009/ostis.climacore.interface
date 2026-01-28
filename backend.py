from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import importlib
import traceback

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)

CORS(app)

UTILS_PACKAGE = "utils"  # имя папки с утилитами

def call_utility(func_name, args):
    try:
        module = importlib.import_module(f"{UTILS_PACKAGE}.{func_name}")
        func = getattr(module, func_name)
        print(f"➡ {func_name}({args})")
        return func(*args)
    except Exception as e:
        print(f"❌ Ошибка при вызове {func_name}")
        traceback.print_exc()
        raise e


@app.route("/api/dispatch", methods=["GET", "POST"])
def dispatch():
    if request.method == "GET":
            from utils.get_all_data import get_all_data

            data = get_all_data()
            return jsonify({
                "status": "success",
                "data": data
            })
    
    data = request.get_json(force=True)

    func_name = data["func"]
    args = data["args"]

    if not func_name:
        return jsonify({"status": "error", "message": "No func provided"}), 400

    try:
        call_utility(func_name, args)
        return jsonify({ "status": "ok" })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/")
def index():
    return send_from_directory('frontend', 'main.html')

if __name__ == "__main__":
    print("🚀 Backend started on http://localhost:2000")
    app.run(host="0.0.0.0", port=2000, debug=True)
