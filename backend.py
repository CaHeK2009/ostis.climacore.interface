from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import importlib
from sc_client.client import connect
import traceback
import json

connect("ws://localhost:8090")

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)

CORS(app)
UTILS_PACKAGE = "utils"


def call_utility(func_name, args):
    try:
        module = importlib.import_module(f"{UTILS_PACKAGE}.{func_name}")
        func = getattr(module, func_name)
        print(f"➡ {func_name}({args})")
        if func_name == "create_measurement":
            for arg in args:
                func(*arg)
            return True
        return func(*args)
    except Exception as e:
        print(f"❌ Ошибка при вызове {func_name}")
        traceback.print_exc()
        raise e


@app.route("/api/dispatch", methods=["GET", "POST"])
def dispatch():
    if request.method == "GET":
        print("📥 GET запрос на получение всех данных")
        try:
            from utils.get_all_data import get_all_data
            data = get_all_data()
            print("✅ Данные успешно получены")
            return jsonify({
                "status": "success",
                "data": data
            })
        except Exception as e:
            print(f"❌ Ошибка при получении данных: {e}")
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    data = request.get_json(force=True)

    func_name = data["func"]
    args = data["args"]

    if not func_name:
        return jsonify({"status": "error", "message": "No func provided"}), 400

    try:
        result = call_utility(func_name, args)
        return jsonify({ 
            "status": "ok",
            "result": result 
        })
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