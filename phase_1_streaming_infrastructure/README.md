# Setting up Kafka and Creating a Topic

All steps are from within the root directory of the repository.

1. Started the Kafka server in the KRaft mode using the command:

   ```bash
   docker run -d --name=kafka -p 9092:9092 apache/kafka
   ```

2. Create a Python virtual environment and activate it
3. Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the create_topic.py script to create the Kafka topic:

   ```bash
   python -m src.create_topic
   ```

# Producing and Consuming the Dataset

1. Run the consumer script in one terminal to start receiving any future messages:

   ```bash
   python -m src.consumer_dataset
   ```

2. In another terminal, run the producer script to start sending rows from the dataset to the Kafka topic:

   ```bash
   python -m src/producer_dataset
   ```

3. You should see the messages being sent by the producer and received by the consumer in their respective terminal windows.
