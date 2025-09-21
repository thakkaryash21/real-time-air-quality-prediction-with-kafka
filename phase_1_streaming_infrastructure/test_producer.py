import json
import time

from kafka import KafkaProducer

from constants import KAFKA_BROKER_URL, KAFKA_TOPIC

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Send 10 dummy messages
for i in range(10):
    msg = {"reading_id": i}
    producer.send(KAFKA_TOPIC, msg)
    print(f"Sent: {msg}")
    time.sleep(1)

producer.flush()
producer.close()
