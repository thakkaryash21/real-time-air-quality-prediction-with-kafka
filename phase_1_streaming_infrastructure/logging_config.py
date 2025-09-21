import logging


def setup_logger(name: str, level=logging.INFO):
    # Global log formatting
    logging.basicConfig(level=level)

    # Reduce verbosity of kafka-python
    logging.getLogger("kafka").setLevel(logging.WARNING)

    return logging.getLogger(name)
