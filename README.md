## QUALITY OF AIR  
### Quantitative Layered Environmental Intelligence System

---

## 1. Overview

**QUALITY OF AIR** is a structured multi-phase environmental monitoring pipeline designed for acquisition, processing and analytical visualization of urban air quality data, combining real sensors, synthetic digital-twin simulation and machine learning–based anomaly detection.

The system is architected as a modular, layered IoT + data-processing framework, emphasizing:

- **Clear separation** between edge sensing, data ingestion, processing and visualization
- **Deterministic transformation stages** from raw readings to analytical indicators
- **Reproducible analytics workflows** over MongoDB-based time series
- **Scalable structural design**, able to ingest both real and simulated data

Rather than a simple sensor dashboard, QUALITY OF AIR implements a sequential processing model composed of independent computational layers.

---

## 2. System Architecture

The system is divided into three macro phases:

- **Phase 1 → Environmental Data Acquisition Layer**
- **Phase 2 → Processing, Indexing & Anomaly Intelligence Layer**
- **Phase 3 → Analytical Visualization & Alerting Layer**

Additionally, auxiliary ingestion interfaces (MQTT bridge and HTTP API) allow integration with heterogeneous IoT setups.

---

## 3. Computational Pipeline

### Phase 1 — Environmental Data Acquisition Layer

Responsible for:

- Reading physical sensors (MQ-135, PMS5003, DHT11) on microcontrollers
- Simulating environmental behavior via a digital twin powered by Random Forests
- Integrating meteorological context (Open-Meteo API)
- Persisting raw readings in MongoDB for downstream analytics

Core components:

- `código sensores/`  
  Low-level Arduino/ESP32 sketches for:
  - MQ-135 gas sensor (`mq_135.ino`)
  - PMS5003 particulate matter sensor focused on PM2.5 (`PMS5003.ino`)
  - DHT11 temperature and humidity sensor (`umidade_temperatura.ino`)

- `simulador.py`  
  Digital twin simulator that:
  - learns typical PM2.5 and gas patterns using `RandomForestRegressor`
  - generates sector-specific readings for different regions of Goiânia
  - enriches data with real-time weather (temperature, humidity, rain proxy)
  - writes structured raw readings into `Monitoramento_do_Ar.Leituras_Sensores` on MongoDB Atlas

- `Codigo_IOT/codigo_MQTT.py`  
  MQTT → MongoDB bridge that:
  - subscribes to HiveMQ Cloud topic(s)
  - decodes JSON payloads from ESP32 devices
  - stores them into a dedicated MongoDB Atlas database for IoT ingestion

- `Codigo_IOT/MongoDB.py`  
  HTTP → MongoDB local API that:
  - receives JSON payloads via REST
  - validates required sensor fields
  - persists them in a local MongoDB instance

All credentials and connection settings are externalized through `config.ini`.

---

### Phase 2 — Processing, Indexing & Anomaly Intelligence Layer

Responsible for:

- Cleaning and structuring raw sensor data
- Computing a unified vectorial pollution index
- Learning “expected” environmental behavior with ML
- Detecting anomalies and health-critical events
- Materializing an analytical snapshot for fast dashboard consumption

Core component:

- `tratamento.py` — **AirQualityPipeline**

Main responsibilities:

- **Data ingestion & cleaning**
  - Reads the latest readings from `Leituras_Sensores`
  - Parses timestamps and enforces numeric types
  - Sorts events chronologically

- **Environmental quality indexing**
  - Derives qualitative labels (Excellent / Good / Moderate / Poor)
  - Computes a **vectorial unified index** combining PM2.5 and gas metrics
  - Enriches with temporal features (hour of day, day of week)

- **Machine learning anomaly intelligence**
  - Trains a `RandomForestRegressor` on recent data to model expected index values
  - Periodically retrains based on configurable intervals
  - Flags anomalies according to:
    - deviation from ML baseline
    - health-based thresholds for the unified index, PM2.5 and gas concentration

- **Analytical snapshot generation**
  - Writes processed records into `Leituras_Analiticas`
  - Keeps this collection as a fast-access analytical view for visual layers

- **Alerting**
  - Detects critical events (index above safety thresholds)
  - Sends HTML e-mail notifications with a configurable cooldown window

Configuration for MongoDB, SMTP and pipeline intervals is centralized in `config.ini`.

---

### Phase 3 — Analytical Visualization & Alerting Layer

Responsible for:

- Aggregation and temporal slicing of environmental indicators
- Map-based inspection of urban air quality
- Comparative visualization between measured and expected (ML) baselines
- Human-readable anomaly exploration

Core component:

- `dash.py` — Streamlit dashboard

Capabilities:

- **Temporal availability panel**: hourly histogram that acts as a time selector
- **Time filters**: date and time-interval filters with zoom-by-selection behavior
- **Spatial filtering**: focus on specific neighborhoods or global city view
- **Unified KPIs**:
  - average unified pollution index
  - average temperature and PM2.5
  - anomaly counts based on ML + rule thresholds
- **3D map (PyDeck)**:
  - fixed coordinates and radii per urban sector for stable visualization
  - color-coded markers by pollution level and classification
- **Temporal evolution plot (Plotly)**:
  - measured unified index vs. ML-expected baseline
- **Per-sector breakdowns**:
  - bar charts for PM2.5 and toxic gases by neighborhood
- **Anomaly table**:
  - reverse-chronological list of critical events with contextual metrics

All visual interactions operate over the analytical view generated by Phase 2.

---

## 4. Design Philosophy

QUALITY OF AIR was designed under the following principles:

- **Modularity** — each layer (acquisition, processing, visualization) is isolated
- **Determinism** — transformations from raw data to analytical outputs are explicit
- **Layer isolation** — changes in the simulator or sensors do not break analytics logic
- **Reproducibility** — simulation and ML steps can be re-executed with the same configuration
- **Expandability** — new sectors, sensors or ML models can be plugged in with minimal coupling

Each phase operates independently and can be refactored or extended without affecting upstream components, as long as MongoDB contracts are respected.

---

## 5. Potential Extensions

The architecture allows seamless integration of:

- Additional ML layers (e.g., forecasting of pollution peaks, clustering of behavioral profiles)
- More sophisticated anomaly scoring (e.g., Isolation Forest, autoencoders)
- Long-term historical storage and roll-up aggregations
- REST/GraphQL APIs on top of the analytical collections
- Real-time streaming ingestion (Kafka / MQTT streaming bridges)
- Public dashboards or city-level reporting portals
- Edge-device management and OTA update orchestration

---

## 6. Academic Positioning

QUALITY OF AIR can be interpreted as a case study in:

- Applied IoT and environmental sensing
- Time-series modeling and anomaly detection
- Layered data engineering and pipeline architecture
- Urban computing and digital-twin simulation
- Integration of physical sensing with ML-based analytical layers

---

## 7. Execution

Example execution flow for the main analytical pipeline:

```bash
pip install -r requirements.txt

# 1. Configure environment (once)
cp config.example.ini config.ini
# -> Fill in MongoDB, SMTP, MQTT and other credentials in config.ini

# 2. (Optional) Start a real-sensor ingestion pipeline
python Codigo_IOT/codigo_MQTT.py         # MQTT → Mongo (HiveMQ → Atlas)
# or
python Codigo_IOT/MongoDB.py             # HTTP API → Mongo local

# 3. Start the digital-twin simulator (Phase 1)
python simulador.py

# 4. Run the processing & anomaly pipeline (Phase 2)
python tratamento.py

# 5. Launch the Streamlit dashboard (Phase 3)
streamlit run dash.py
```

Each component can be run independently for testing or integrated into a long-running deployment using process managers or containerization.


