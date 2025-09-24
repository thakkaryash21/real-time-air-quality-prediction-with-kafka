import os
import pandas as pd

from ..utils.model_utils import evaluate
from ..utils.logging_config import setup_logger
from ..utils.constants import TRAINING_DATA_PATH

logger = setup_logger(os.path.basename(__file__))

TRAIN_SPLIT_RATIO = 0.8
TARGET = "CO(GT)"
SEASONAL_PERIOD = 24  # hourly -> daily seasonality


def main():
    logger.info("Loading dataset...")
    df = pd.read_csv(TRAINING_DATA_PATH, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    df = df.asfreq("h")
    y = df[TARGET].dropna()

    split_idx = int(len(y) * TRAIN_SPLIT_RATIO)
    train, val = y.iloc[:split_idx], y.iloc[split_idx:]

    # Create predictions using seasonal naive approach
    # For each hour, use the value from the same hour 24 hours ago
    y_pred = val.copy()

    # For the first 24 hours, use the last 24 hours of training data
    y_pred.iloc[:SEASONAL_PERIOD] = train.iloc[-SEASONAL_PERIOD:].values

    # For the rest, use values from 24 hours earlier in the validation set
    for i in range(SEASONAL_PERIOD, len(val)):
        y_pred.iloc[i] = val.iloc[i - SEASONAL_PERIOD]

    metrics = evaluate(val, y_pred)
    logger.info(f"Seasonal naive (t-24) metrics: {metrics}")


if __name__ == "__main__":
    main()
