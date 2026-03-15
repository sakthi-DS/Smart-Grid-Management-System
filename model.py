import pandas as pd
import joblib

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# Load dataset

data = pd.read_csv("data/grid_data.csv")

# FIXED datetime parsing
data["time"] = pd.to_datetime(data["time"])

data["hour"] = data["time"].dt.hour
data["day"] = data["time"].dt.day
data["month"] = data["time"].dt.month

# Demand column

data["demand"] = data["ev_load"] + data["house_demand"]

data["future_demand"] = data["demand"].shift(-1)

data = data.dropna()

# SOLAR MODEL

solar_features = [
    "hour",
    "temperature",
    "cloud_cover",
    "solar_radiation"
]

X_solar = data[solar_features]
y_solar = data["solar"]

X_train, X_test, y_train, y_test = train_test_split(
    X_solar, y_solar, test_size=0.2
)

solar_model = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1
)

solar_model.fit(X_train, y_train)

solar_pred = solar_model.predict(X_test)

print("\nSolar Model R2:", r2_score(y_test, solar_pred))

# WIND MODEL

wind_features = [
    "wind_speed",
    "hour"
]

X_wind = data[wind_features]
y_wind = data["wind"]

X_train, X_test, y_train, y_test = train_test_split(
    X_wind, y_wind, test_size=0.2
)

wind_model = XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1
)

wind_model.fit(X_train, y_train)

wind_pred = wind_model.predict(X_test)

print("Wind Model R2:", r2_score(y_test, wind_pred))


# DEMAND MODEL (Improved)

data["ev_lag1"] = data["ev_load"].shift(1)
data["house_lag1"] = data["house_demand"].shift(1)
data["demand_lag1"] = data["demand"].shift(1)

data = data.dropna()

demand_features = [
    "ev_load",
    "house_demand",
    "temperature",
    "hour",
    "day",
    "month",
    "ev_lag1",
    "house_lag1",
    "demand_lag1"
]

X_demand = data[demand_features]
y_demand = data["future_demand"]

X_train, X_test, y_train, y_test = train_test_split(
    X_demand, y_demand, test_size=0.2
)

demand_model = XGBRegressor(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.08
)

demand_model.fit(X_train, y_train)

pred = demand_model.predict(X_test)

print("Demand Model R2:", r2_score(y_test, pred))

# Save models

joblib.dump(solar_model, "solar_model.pkl")
joblib.dump(wind_model, "wind_model.pkl")
joblib.dump(demand_model, "demand_model.pkl")

print("\nModels saved successfully!")