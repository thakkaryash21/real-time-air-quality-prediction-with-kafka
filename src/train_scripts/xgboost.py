import os
import pandas as pd
import xgboost as xgb

from ..utils.feature_utils import (
    add_lag_features,
    add_rolling_features,
    add_cyclical_time_features,
)
from ..utils.model_utils import save_model, evaluate, XGB_LAGS, XGB_ROLLS
from ..utils.logging_config import setup_logger
from ..utils.constants import TRAINING_DATA_PATH, XGB_MODEL_PATH

logger = setup_logger(os.path.basename(__file__))

# Paths
TRAIN_SPLIT_RATIO = 0.8
TARGET = "CO(GT)"


def create_features(df):
    # Add lag/rolling features for each feature column except target
    feature_cols = [col for col in df.columns if col != TARGET]

    for col in feature_cols:
        df = add_lag_features(df, col, lags=XGB_LAGS)
        df = add_rolling_features(df, col, windows=XGB_ROLLS)

    df = add_cyclical_time_features(df)

    # Impute missing feature values
    df = df.ffill()

    return df


def main():
    # Load training data
    logger.info("Loading dataset...")
    df = pd.read_csv(TRAINING_DATA_PATH, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)

    # Drop rows with missing target only
    df = df.dropna(subset=[TARGET])

    # Feature engineering
    logger.info("Creating features...")
    df = create_features(df)
    feature_cols = [col for col in df.columns if col != TARGET]

    # Train-validation split (time-based)
    split_idx = int(len(df) * TRAIN_SPLIT_RATIO)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]

    X_train, y_train = train_df[feature_cols], train_df[TARGET]
    X_val, y_val = val_df[feature_cols], val_df[TARGET]

    # Train XGBoost model
    logger.info("Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_val)
    metrics = evaluate(y_val, y_pred)
    logger.info(f"Validation metrics: {metrics}")

    # Save model
    save_model(model, XGB_MODEL_PATH)
    logger.info(f"XGBoost model saved to {XGB_MODEL_PATH}")


if __name__ == "__main__":
    main()
