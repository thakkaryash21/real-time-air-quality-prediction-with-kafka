# Phase 1 Documentation

## Overview

Phase 1 sets up the streaming infrastructure using Apache Kafka. A producer streams rows from the UCI Air Quality dataset into a Kafka topic, and a consumer receives, cleans, and stores them for downstream analysis.

## Design Choices and Rationale

### Kafka in KRaft Mode

- Used the official `apache/kafka` Docker image with KRaft (Kafka Raft metadata mode), no ZooKeeper.
- **Why**:
  - **Simplicity**: Fewer moving parts compared to ZooKeeper-based deployments.
  - **Industry Standard**: KRaft is the default in newer Kafka versions and aligns with industry direction.

### Producer

- Streams dataset rows one at a time with a 1-second delay, sending `datetime` as ISO 8601 strings.
- **Why**:
  - **Real-Time Simulation**: The dataset is historical; the delay mimics sensor data streaming in real time.
  - **Lightweight Design**: Producer is only responsible for sending the sensor data, avoiding cleaning or transformation. This separation of concerns simplifies the architecture and makes each component easier to maintain in production.
  - **Serialization Safety**: Converting `datetime` to ISO 8601 avoids JSON serialization errors with Pandas Timestamps.

### Consumer

- Reads from Kafka, converts `datetime` strings back into Pandas datetimes, replaces faulty values (`-200`) with `NaN`, and appends messages to a DataFrame in batches.
- **Why**:
  - **Centralized Cleaning**: All the cleaning, validation and transformation logic is in one place, making it easier to manage and update.
  - **Faulty Values**: The dataset encodes missing values as `-200`. Converting these to `NaN` ensures compatibility with Pandas operations.
  - **Batching**: Buffering and appending in chunks (`APPEND_SIZE`) is more efficient than appending rows one at a time.
  - **Datetime Conversion**: Ensures downstream time-series analysis can leverage Pandas’ datetime functionality.

### Logging

- Centralized logging configuration (`logging_config.py`) reduces Kafka client verbosity and provides consistent formatting across producer and consumer.
- **Why**:
  - **Clarity**: Suppressing noisy Kafka client logs highlights relevant application messages.
  - **Consistency**: Shared logger setup ensures both producer and consumer use the same log structure.
  - **Better than Print Statements**: Unlike `print`, logging supports log levels (INFO, WARNING, ERROR), timestamps, configurable formats, and can easily be redirected to files or monitoring systems. This makes it much more suitable for debugging and production-like environments.

## Challenges and Solutions

- **Unnamed Columns**: UCI dataset includes empty trailing columns (`Unnamed: 15`, `Unnamed: 16`). These were dropped in the producer because they contain no useful sensor data.
- **Faulty Values**: Missing readings marked as `-200` were normalized in the consumer.
- **Timestamps**: Pandas `Timestamp` objects are not JSON serializable; converting them to ISO 8601 strings in the producer avoided runtime errors.
