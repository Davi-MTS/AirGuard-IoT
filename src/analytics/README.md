# Analytics Layer

This module contains the processing and anomaly detection pipeline for air quality data:

- `pipeline.py` — end-to-end pipeline that:
  - reads raw readings from MongoDB,
  - computes unified air quality indices,
  - applies a RandomForest-based anomaly model,
  - writes analytical views for the dashboard,
  - and triggers email alerts for critical events.

