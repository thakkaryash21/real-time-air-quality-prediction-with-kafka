import json
import os
import pandas as pd
from kafka import KafkaConsumer

from .utils.constants import (
    KAFKA_BROKER_URL,
    KAFKA_TOPIC,
    FAULTY_VALUE,
    XGB_MODEL_PATH,
)
from .utils.logging_config import setup_logger
from .train_scripts.xgboost import create_features
from .utils.model_utils import load_model, XGB_LAGS, XGB_ROLLS

logger = setup_logger(os.path.basename(__file__))

# Load trained model
model = load_model(XGB_MODEL_PATH)
logger.info(f"Loaded XGBoost model from {XGB_MODEL_PATH}")

# Containers
history_df = pd.DataFrame()
# Warm-up period based on lags/rolls
WARMUP_STEPS = max(max(XGB_LAGS), max(XGB_ROLLS))

TARGET_COL = "CO(GT)"


def clean_record(record):
    cleaned = {}
    for k, v in record.items():
        if k == "datetime":
            cleaned[k] = pd.to_datetime(v, errors="coerce")
        elif isinstance(v, (int, float)) and v == FAULTY_VALUE:
            cleaned[k] = pd.NA
        else:
            cleaned[k] = v
    return cleaned


def main():
    global history_df

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="air_quality_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    logger.info(f"Subscribed to topic: {KAFKA_TOPIC}")

    try:
        for message in consumer:
            record = clean_record(message.value)
            logger.debug(f"Received: {record}")

            # Append new row
            history_df = pd.concat(
                [history_df, pd.DataFrame([record])], ignore_index=True
            )
            history_df.set_index("datetime", inplace=True)
            history_df.sort_index(inplace=True)

            # Wait until we have enough history
            if len(history_df) < WARMUP_STEPS:
                continue

            # Get raw target before imputation
            y_true = record.get(TARGET_COL, pd.NA)

            # Feature engineering
            feat_df = create_features(history_df.copy())
            latest = feat_df.iloc[[-1]]

            # Drop target before prediction
            feature_cols = [c for c in latest.columns if c != TARGET_COL]
            X_latest = latest[feature_cols]

            # Predict
            y_pred = model.predict(X_latest)[0]

            if pd.notna(y_true):
                logger.info(
                    f"Prediction at {record['datetime']}: {y_pred:.4f} | Actual: {y_true}"
                )
            else:
                logger.info(
                    f"Prediction at {record['datetime']}: {y_pred:.4f} | Actual missing"
                )

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")

    finally:
        consumer.close()
        logger.info("Consumer closed")


if __name__ == "__main__":
    main()
