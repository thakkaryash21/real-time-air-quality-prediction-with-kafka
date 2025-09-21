## Phase 1 - Setup

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
   python phase_1_streaming_infrastructure/create_topic.py
   ```

5. Verify the topic creation by sending and receiving messages using the following in two separate terminal windows:
   ```bash
   python -m phase_1_streaming_infrastructure.test_consumer
   python -m phase_1_streaming_infrastructure.test_producer
   ```

The receiver terminal should display the messages sent from the sender terminal, confirming that the Kafka topic is set up correctly.
