from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import configparser
import os

app = Flask(__name__)

# --- MONGODB CONNECTION ---
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")
config.read(config_path, encoding="utf-8")

MONGO_URI = config.get("MongoLocal", "uri", fallback="mongodb://localhost:27017/")
DB_NAME = config.get("MongoLocal", "db", fallback="IOTIA2")
COLLECTION_NAME = config.get("MongoLocal", "collection_sensores", fallback="sensores")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


@app.route("/", methods=["GET"])
def home():
    return "API server is ON — send POST data to /api/sensors"


@app.route("/api/sensors", methods=["POST"])
def save_data():
    try:
        data = request.get_json()

        expected_fields = ["temperatura", "umidade_ar", "umidade_solo"]
        for field in expected_fields:
            if field not in data:
                return jsonify({"error": f"Field '{field}' is missing in JSON"}), 400

        data["created_at"] = datetime.now()

        result = collection.insert_one(data)

        data.pop("_id", None)
        data["created_at"] = data["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return jsonify(
            {
                "message": "Data received and stored successfully.",
                "id": str(result.inserted_id),
                "data": data,
            }
        ), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="192.168.1.103", port=8080, debug=True)

