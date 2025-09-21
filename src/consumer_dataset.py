import json
import os
import pandas as pd
from kafka import KafkaConsumer
from .constants import KAFKA_BROKER_URL, KAFKA_TOPIC, FAULTY_VALUE
from .logging_config import setup_logger


logger = setup_logger(os.path.basename(__file__))


def clean_record(record):
    cleaned = {}
    for k, v in record.items():
        # Convert datetime string back to pandas datetime
        if k == "datetime":
            cleaned[k] = pd.to_datetime(v, errors="coerce")

        # Replace FAULTY_VALUE with NaN for non-numeric fields if needed
        elif isinstance(v, (int, float)) and v == FAULTY_VALUE:
            cleaned[k] = pd.NA

        else:
            cleaned[k] = v
    return cleaned


def main():
    # 1. Setup consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset="latest",  # read from latest messages
        enable_auto_commit=True,
        group_id="air_quality_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    logger.info(f"Subscribed to topic: {KAFKA_TOPIC}")

    # 2. Container for streamed data
    df = pd.DataFrame()
    records = []
    APPEND_SIZE = 100  # Number of records to append at once

    # 3. Consume loop
    try:
        for message in consumer:
            record = message.value

            # Ensure that the row is not empty
            if not record:
                continue

            # Clean the record
            cleaned = clean_record(record)
            records.append(cleaned)

            logger.info(f"Received: {cleaned}")

            # Append to DataFrame only after collecting APPEND_SIZE records
            if len(records) >= APPEND_SIZE:
                df = pd.concat([df, pd.DataFrame(records)], ignore_index=True)
                records = []

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")

    finally:
        consumer.close()
        logger.info("Consumer closed")


if __name__ == "__main__":
    main()
