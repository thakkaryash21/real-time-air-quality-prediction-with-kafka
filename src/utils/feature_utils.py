import numpy as np


def add_lag_features(df, col, lags=[1, 24]):
    for lag in lags:
        df[f"{col}_lag{lag}"] = df[col].shift(lag)
    return df


def add_rolling_features(df, col, windows=[3, 24]):
    for w in windows:
        df[f"{col}_roll{w}"] = df[col].rolling(window=w).mean()
    return df


def add_cyclical_time_features(df):
    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.dayofweek

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

    return df
