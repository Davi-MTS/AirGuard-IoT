# Ingestion Layer

This module contains the services responsible for ingesting sensor data into MongoDB:

- `mqtt_bridge.py` — MQTT → MongoDB bridge (HiveMQ Cloud to MongoDB Atlas)
- `http_api.py` — HTTP REST API → MongoDB local

