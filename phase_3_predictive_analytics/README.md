# Phase 3 - Predictive Analytics and Real-Time Inference

This phase develops and evaluates predictive models for air quality forecasting and integrates the best-performing model into the real-time Kafka streaming pipeline for live predictions.

## Prerequisites

1. Ensure you have completed Phase 1 (Kafka streaming infrastructure) and Phase 2 (EDA)
2. Make sure you have a Python virtual environment activated with required packages installed:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the training and test datasets are available:

   - `src/data/train.csv` (generated from Phase 2)
   - `src/data/test.csv` (generated from Phase 2)

4. Ensure Kafka server is running:

   ```bash
   docker run -d --name=kafka -p 9092:9092 apache/kafka
   ```

## Model Training

Before running the real-time prediction system, you need to train the predictive models. Run the following scripts in order to train different models and compare their performance:

### 1. Baseline Seasonal Model

```bash
python -m src.train_scripts.baseline_seasonal
```

This will:

- Implements a seasonal naive approach using 24-hour periodicity
- For each hour, predicts using the value from the same hour 24 hours ago
- Serves as a simple baseline to compare against more sophisticated models
- Evaluates performance using RMSE, MAE, and R² metrics

### 2. SARIMA Model

```bash
python -m src.train_scripts.sarima
```

This will:

- Trains a Seasonal ARIMA model using auto-ARIMA for parameter selection
- Uses 24-hour seasonal period to capture daily patterns
- Automatically determines optimal (p,d,q)(P,D,Q,m) parameters
- Saves the trained model to `src/models/sarima_co.pkl`
- Evaluates performance on validation set

### 3. XGBoost Model (Recommended)

```bash
python -m src.train_scripts.xgboost
```

This will:

- Perform comprehensive feature engineering:
  - Lag features: 1, 2, and 24-hour lags to capture temporal dependencies
  - Rolling features: 3-hour and 24-hour moving averages for trend smoothing
  - Cyclical features: Hour-of-day and day-of-week encoded with sine/cosine
- Train XGBoost regressor with optimized hyperparameters:
  - 500 estimators with 0.05 learning rate for balanced performance
  - Max depth of 5 to prevent overfitting
  - Subsampling for regularization
- Save the trained model to `src/models/xgboost_co.pkl`
- Provide the best performance (RMSE: 0.90, R²: 0.70)

## Model Performance Comparison

After running all training scripts, you should see performance metrics similar to:

| Model               | RMSE | MAE  | R²    |
| ------------------- | ---- | ---- | ----- |
| XGBoost             | 0.90 | 0.58 | 0.70  |
| SARIMA (Auto-ARIMA) | 1.84 | 1.54 | –0.23 |
| Seasonal Naive      | 1.69 | 1.24 | –0.04 |

**XGBoost** significantly outperforms other models and is used for real-time predictions.

## Real-Time Prediction System

1. **Run the consumer script** in one terminal to start receiving messages and making predictions:

   ```bash
   python -m src.consumer_dataset
   ```

   **What the consumer does:**

   - Loads the pre-trained XGBoost model
   - Subscribes to the `air_quality` Kafka topic
   - For each incoming message:
     - Cleans and preprocesses the data
     - Builds a feature history buffer for lag/rolling calculations
     - Applies the same feature engineering pipeline used in training
     - Makes real-time CO(GT) predictions using the XGBoost model
     - Logs predictions alongside actual values (when available)
   - Requires a warm-up period of 24 records to generate lag/rolling features

2. **In another terminal**, run the producer script to start streaming the test dataset:

   ```bash
   python -m src.producer_dataset
   ```

   **What the producer does:**

   - Streams rows from `src/data/test.csv` to the Kafka topic
   - Sends one record every 0.5 seconds to simulate real-time data flow
   - Converts datetime to ISO format for JSON serialization
   - Handles any serialization errors gracefully

3. **Expected Output:**
   You should see messages being sent by the producer and received by the consumer with real-time predictions. Example consumer output:
   ```
    INFO:consumer_dataset.py:Loaded XGBoost model from src/models/xgboost_co.pkl
    INFO:consumer_dataset.py:Subscribed to topic: air_quality
    INFO:consumer_dataset.py:Prediction at 2005-01-23 11:00:00: 3.5908 | Actual missing
    INFO:consumer_dataset.py:Prediction at 2005-01-24 18:00:00: 3.6916 | Actual: 1.5
   ```

## System Architecture

The real-time prediction system consists of:

1. **Kafka Producer**: Streams test data to simulate incoming sensor readings
2. **Kafka Topic**: `air_quality` topic for message buffering
3. **Kafka Consumer**: Processes messages and generates predictions
