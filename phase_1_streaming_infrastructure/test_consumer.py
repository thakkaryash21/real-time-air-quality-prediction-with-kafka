import json

from kafka import KafkaConsumer

from constants import (
    KAFKA_BROKER_URL,
    KAFKA_CONSUMER_CLIENT_ID,
    KAFKA_CONSUMER_GROUP_ID,
    KAFKA_TOPIC,
)

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER_URL,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=KAFKA_CONSUMER_GROUP_ID,
    client_id=KAFKA_CONSUMER_CLIENT_ID,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)

print("Listening for messages...")
for message in consumer:
    print(f"Received: {message.value}")
