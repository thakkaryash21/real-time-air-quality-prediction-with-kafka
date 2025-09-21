import pandas as pd
import os
import time
import json
from kafka import KafkaProducer
from constants import KAFKA_BROKER_URL, KAFKA_TOPIC, DATASET_PATH
from .logging_config import setup_logger

logger = setup_logger(os.path.basename(__file__))

# 1. Load dataset
df = pd.read_csv(DATASET_PATH, sep=";", decimal=",")
# Drop empty columns from the dataset. Without the column name, they may not represent
# useful information. So, dropping them
df = df.dropna(axis=1, how="all")

# Combine Date and Time into a single datetime column
df["datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"], format="%d/%m/%Y %H.%M.%S"
)
df.drop(columns=["Date", "Time"], inplace=True)

# 2. Setup producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# 3. Stream rows
try:
    for _, row in df.iterrows():
        try:
            msg = row.to_dict()
            msg["datetime"] = msg["datetime"].isoformat()
            producer.send(KAFKA_TOPIC, msg)
            logger.info(f"Sent: {msg}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

        time.sleep(1)  # Simulate real-time by waiting 1 second between messages
except KeyboardInterrupt:
    logger.info("Producer interrupted by user")
finally:
    producer.flush()
    producer.close()
