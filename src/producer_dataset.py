import pandas as pd
import os
import time
import json
from kafka import KafkaProducer
from .utils.constants import KAFKA_BROKER_URL, KAFKA_TOPIC, TESTING_DATA_PATH
from .utils.logging_config import setup_logger

logger = setup_logger(os.path.basename(__file__))

# 1. Load dataset
df = pd.read_csv(TESTING_DATA_PATH, parse_dates=["datetime"])

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
