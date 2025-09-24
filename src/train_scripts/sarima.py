import os
import pandas as pd
import pmdarima as pm

from ..utils.model_utils import save_model, evaluate
from ..utils.logging_config import setup_logger
from ..utils.constants import TRAINING_DATA_PATH, SARIMA_MODEL_PATH
import warnings

logger = setup_logger(os.path.basename(__file__))
# Suppress warnings from pmdarima
warnings.filterwarnings("ignore", category=FutureWarning)

TRAIN_SPLIT_RATIO = 0.8  # 80% train, 20% validation
TARGET = "CO(GT)"


def main():
    # 1. Load training data
    logger.info("Loading dataset...")
    df = pd.read_csv(TRAINING_DATA_PATH, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    df = df.asfreq("h")  # Ensure hourly frequency

    series = df[TARGET].dropna()

    # 2. Train-validation split (time-based)
    split_idx = int(len(series) * TRAIN_SPLIT_RATIO)
    train, val = series.iloc[:split_idx], series.iloc[split_idx:]

    # 3. Run auto-ARIMA search
    logger.info("Running auto-ARIMA search...")
    model = pm.auto_arima(
        train,
        seasonal=True,
        m=24,  # daily seasonality
        stepwise=True,
        suppress_warnings=True,
        error_action="ignore",
        max_p=3,
        max_q=3,
        max_d=1,
        max_P=1,
        max_Q=1,
        max_D=1,
        trace=True,
    )

    logger.info(
        f"Selected order: {model.order}, seasonal_order: {model.seasonal_order}"
    )

    # 4. Forecast on validation set
    n_periods = len(val)
    y_pred = model.predict(n_periods=n_periods)
    y_true = val

    # 5. Evaluate
    metrics = evaluate(y_true, y_pred)
    logger.info(f"Validation metrics: {metrics}")

    # 6. Save model
    save_model(model, SARIMA_MODEL_PATH)
    logger.info(f"Auto-ARIMA model saved to {SARIMA_MODEL_PATH}")


if __name__ == "__main__":
    main()
