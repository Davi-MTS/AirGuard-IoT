import json
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
import ssl
import time
import configparser
import os

#============================
# LOAD CONFIG FROM ROOT config.ini
#============================
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")
config.read(config_path, encoding="utf-8")

#============================
# MONGODB ATLAS CONFIG
#============================
MONGO_URI = config.get("MongoIot", "uri")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[config.get("MongoIot", "db", fallback="iot_db")]
collection = db[config.get("MongoIot", "collection_raw", fallback="leituras_brutas")]  # raw data collection

#============================
# MQTT (HIVEMQ CLOUD) CONFIG
#============================
MQTT_BROKER = config.get("MQTT", "broker")
MQTT_PORT = config.getint("MQTT", "port")
MQTT_USER = config.get("MQTT", "user")
MQTT_PASS = config.get("MQTT", "password")

MQTT_TOPIC = config.get("MQTT", "topic")


#============================
# CALLBACK: on connect
#============================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] Connected to HiveMQ!")
        client.subscribe(MQTT_TOPIC)
        print(f"[OK] Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"[ERROR] Connection failed. Code: {rc}")


#============================
# CALLBACK: on message
#============================
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        # Add reception timestamp
        data["received_at"] = datetime.utcnow()

        # Save to MongoDB Atlas
        collection.insert_one(data)

        print(f"[MongoDB] Inserted: {data}")

    except json.JSONDecodeError:
        print("[ERROR] Received message is not valid JSON:")
        print(msg.payload.decode())

    except Exception as e:
        print("[ERROR] Failed to save to Mongo or process message:", e)


#============================
# CREATE MQTT CLIENT
#============================
client = mqtt.Client()

client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

client.on_connect = on_connect
client.on_message = on_message


#============================
# MAIN LOOP WITH RECONNECT
#============================
if __name__ == "__main__":
    while True:
        try:
            print("[INFO] Connecting to HiveMQ...")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_forever()

        except Exception as e:
            print("[ERROR] Connection lost. Reconnecting in 5 seconds...")
            print("Details:", e)
            time.sleep(5)


