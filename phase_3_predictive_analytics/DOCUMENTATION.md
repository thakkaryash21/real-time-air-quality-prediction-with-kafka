# Phase 3: Predictive Modeling and Deployment Report

## Executive Summary

Phase 3 develops and evaluates predictive models for the UCI Air Quality dataset within the Kafka-based streaming pipeline. Models considered:

- **Naive and Seasonal Naive (t–1, t–24)** baselines for performance benchmarking.
- **SARIMA (Auto-ARIMA)** as a classical statistical baseline.
- **XGBoost** with engineered temporal features (lags, rolling statistics, cyclical encodings).

Key findings:

- **XGBoost** achieved the best validation performance (RMSE: 0.90, R²: 0.70), significantly outperforming SARIMA and baselines.
- **SARIMA** struggled with pollutant non-stationarity and delivered weak metrics (RMSE: 1.84, R²: –0.23).
- **Seasonal Naive baseline** performed poorly (RMSE: 1.69, R²: –0.04), showing that simplistic persistence models cannot capture longer-term dependencies.

The XGBoost model was integrated into the real-time consumer for production inference. Deployment considerations include feature consistency, monitoring, drift detection, and retraining pipelines.

## 1. Feature Engineering

Feature engineering leveraged temporal and contextual signals identified in Phase 2:

- **Lagged Features:** `lag1`, `lag2`, `lag24` to capture immediate and daily pollutant persistence.
- **Rolling Features:** 3-hour (`roll3`) and 24-hour (`roll24`) moving averages to smooth noise and model temporal context.
- **Cyclical Encodings:** Hour-of-day and day-of-week encoded with sine/cosine transformations to represent periodicity.

Implementation:

- Centralized in `feature_utils.py`, ensuring reusable and consistent transformations.
- Applied identically in both training (`xgboost.py`) and streaming consumer (`consumer_dataset.py`).
- Missing values handled with forward-fill imputation during training; streaming consumer preserves `NaN` consistency with raw feed.

## 2. Model Development and Technical Implementation

### XGBoost

- **Train/validation split:** 80/20, time-based to prevent leakage.
- **Hyperparameters:**
  - `n_estimators = 500`: Large number of boosting rounds to capture long-term dependencies.
  - `learning_rate = 0.05`: Balanced training stability with model expressiveness; slower learning rate required more trees but improved generalization.
  - `max_depth = 5`: Limited tree complexity to reduce overfitting while still capturing nonlinear feature interactions.
  - `subsample = 0.8`, `colsample_bytree = 0.8`: Introduced randomness to improve robustness and prevent overfitting.
- **Evaluation:** Outperformed all baselines with strong generalization.

### SARIMA

- Implemented in `sarima.py` using `pmdarima.auto_arima`.
- Seasonal period `m=24` for daily cycles.
- Found optimal order `(2,1,1)(1,0,1,24)`.
- Validation performance significantly weaker than XGBoost.

### Baselines

- **Naive (t–1):** Previous observation as prediction.
- **Seasonal Naive (t–24):** Previous day’s value at same hour.

### Utilities

- **`model_utils.py`**: provides `save_model`, `load_model`, and unified `evaluate` with RMSE/MAE/R².

## 3. Performance Analysis and Comparative Assessment

### Metrics (Validation Phase)

| Model               | RMSE | MAE  | R²    |
| ------------------- | ---- | ---- | ----- |
| XGBoost             | 0.90 | 0.58 | 0.70  |
| SARIMA (Auto-ARIMA) | 1.84 | 1.54 | –0.23 |
| Seasonal Naive      | 1.69 | 1.24 | –0.04 |

### Comparative Assessment

- **XGBoost:** Best overall performance; captured nonlinear pollutant-weather relationships and temporal dependencies.
- **SARIMA:** Underperformed due to non-stationarity, irregular pollutant spikes, and inability to handle exogenous regressors effectively.
- **Baselines:** Useful as sanity checks but too simplistic. Seasonal Naive failed to generalize beyond daily persistence.

### Qualitative Significance

Even without statistical hypothesis testing, the differences in RMSE and R² across models are large enough to conclude that XGBoost offers meaningful improvements in predictive accuracy and practical usability.

## 4. Production Integration and Deployment Strategy

### Streaming Integration

- **Producer:** Streams rows from the test dataset into the Kafka topic.
- **Consumer:**
  - Cleans incoming records (`datetime` conversion, faulty value handling).
  - Applies same feature engineering pipeline used in training.
  - Runs inference with saved XGBoost model (`xgboost_co.pkl`).
  - Logs predictions alongside actual values in real time.

### Monitoring & Retraining when deployed in Production

- **Prediction Logging:** Store predictions vs actuals for live evaluation.
- **Drift Detection:** Monitor error distributions and use statistical tests to detect shifts.
- **Retraining Strategy:** Hybrid approach:
  - **Schedule-based:** retrain weekly/monthly using latest data. This is required to adapt to seasonal trends and evolving patterns.
  - **Trigger-based:** retrain if live R² drops below a set threshold. This also ensures responsiveness to sudden changes.
- **CI/CD & Deployment:**
  - Containerize producer/consumer with Docker.
  - Deploy via Kubernetes for horizontal scaling.
  - Use Kafka monitoring tools (Confluent Control Center or Grafana) for end-to-end observability.
