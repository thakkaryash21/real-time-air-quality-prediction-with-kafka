KAFKA_BROKER_URL = "localhost:9092"
KAFKA_TOPIC = "air_quality"
KAFKA_NUM_PARTITIONS = 1
KAFKA_REPLICATION_FACTOR = 1
KAFKA_CLIENT_ID = "air_quality_admin"
KAFKA_PRODUCER_CLIENT_ID = "air_quality_producer"
KAFKA_CONSUMER_GROUP_ID = "air_quality_consumer_group"
KAFKA_CONSUMER_CLIENT_ID = "air_quality_consumer"

FAULTY_VALUE = -200

TRAINING_DATA_PATH = "src/data/train.csv"
TESTING_DATA_PATH = "src/data/test.csv"

MODEL_DIR = "src/models"
XGB_MODEL_PATH = f"{MODEL_DIR}/xgboost_co.pkl"
SARIMA_MODEL_PATH = f"{MODEL_DIR}/sarima_co.pkl"
