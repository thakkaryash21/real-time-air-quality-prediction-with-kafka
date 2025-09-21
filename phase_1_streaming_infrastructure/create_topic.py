from kafka.admin import KafkaAdminClient, NewTopic

from constants import (
    KAFKA_BROKER_URL,
    KAFKA_CLIENT_ID,
    KAFKA_NUM_PARTITIONS,
    KAFKA_REPLICATION_FACTOR,
    KAFKA_TOPIC,
)

# Connect to the Kafka Broker
admin_client = KafkaAdminClient(
    bootstrap_servers=KAFKA_BROKER_URL, client_id=KAFKA_CLIENT_ID
)

#  Define the topic
topic = NewTopic(
    name=KAFKA_TOPIC,
    num_partitions=KAFKA_NUM_PARTITIONS,
    replication_factor=KAFKA_REPLICATION_FACTOR,
)

# Create the topic
try:
    admin_client.create_topics(new_topics=[topic], validate_only=False)
    print(f"Topic '{KAFKA_TOPIC}' created successfully.")
except Exception as e:
    print(f"Failed to create topic '{KAFKA_TOPIC}': {e}")
finally:
    admin_client.close()
