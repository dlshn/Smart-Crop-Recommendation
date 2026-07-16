import os
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# dataset.csv is located at the repository root `data/`, not under backend/service/
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'data', 'dataset.csv')
MODEL_DIR = os.path.join(BASE_DIR, '..', 'models')

FEATURES = ['district', 'month', 'day_of_year', 'temperature', 'rainfall', 'humidity']

_DATA_CACHE = None
_MODEL_CACHE = {}


def load_data():
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE

    # read with latin1 to be tolerant of degree symbol encodings
    df = pd.read_csv(DATA_PATH, encoding='latin1', low_memory=False)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date', 'Region'])
    df['district'] = df['Region'].str.strip()
    df['month'] = df['Date'].dt.month
    df['day_of_year'] = df['Date'].dt.dayofyear

    # Robust column detection: headers may include odd characters for ° (degree)
    def find_col(cols, keywords):
        for k in keywords:
            for c in cols:
                if k.lower() in c.lower():
                    return c
        return None

    cols = df.columns.tolist()
    temp_col = find_col(cols, ['temperature', 'temp', '°c', 'c)'])
    rain_col = find_col(cols, ['rainfall', 'rain'])
    hum_col = find_col(cols, ['humidity', 'humid'])
    price_col = find_col(cols, ['fruit_price', 'fruit price', 'price per unit', 'price'])

    if temp_col is None or rain_col is None or hum_col is None or price_col is None:
        raise RuntimeError(f"Required columns not found. Detected columns: {cols}")

    df['temperature'] = pd.to_numeric(df[temp_col], errors='coerce')
    df['rainfall_mm'] = pd.to_numeric(df[rain_col], errors='coerce')
    df['humidity'] = pd.to_numeric(df[hum_col], errors='coerce')
    df['price'] = pd.to_numeric(df[price_col], errors='coerce')

    if 'rainfall' not in df.columns:
        df['rainfall'] = df['rainfall_mm']

    _DATA_CACHE = df.dropna(subset=['temperature', 'rainfall', 'humidity', 'price'])
    return _DATA_CACHE


def train_price_model(crop=None):
    df = load_data()
    if 'fruit_Commodity' not in df.columns:
        raise RuntimeError('fruit_Commodity column is required for crop-aware training')

    if crop:
        df = df[df['fruit_Commodity'].astype(str).str.lower() == str(crop).strip().lower()]
    else:
        df = df[df['fruit_Commodity'].isin(df['fruit_Commodity'].dropna().unique())]

    if df.empty:
        raise RuntimeError(f'No data found for crop: {crop}')

    df = df.rename(columns={'fruit_Commodity': 'crop'})
    df['price'] = df['price'].fillna(df['price'].median())
    if 'rainfall' not in df.columns:
        df['rainfall'] = df['rainfall_mm']

    X = df[['district', 'month', 'day_of_year', 'temperature', 'rainfall', 'humidity']]
    X = pd.get_dummies(X, columns=['district', 'month'], drop_first=True)
    y = df['price']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    rmse = float(np.sqrt(mse))
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_name = str(crop).lower().replace(' ', '_') if crop else 'all'
    model_path = os.path.join(MODEL_DIR, f'price_model_{model_name}.joblib')
    joblib.dump(model, model_path)
    print(f'Model trained for {crop or "all crops"}. RMSE:', rmse)
    return model, model_path


_MODEL_LOCK = threading.RLock()


def load_model(crop=None):
    model_name = str(crop).lower().replace(' ', '_') if crop else 'all'
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]

    with _MODEL_LOCK:
        # Another thread may have populated this while we waited for the lock.
        if model_name in _MODEL_CACHE:
            return _MODEL_CACHE[model_name]

        model_path = os.path.join(MODEL_DIR, f'price_model_{model_name}.joblib')
        if os.path.exists(model_path):
            try:
                result = joblib.load(model_path), model_path
                _MODEL_CACHE[model_name] = result
                return result
            except Exception:
                os.remove(model_path)

        try:
            result = train_price_model(crop=crop)
        except Exception:
            # No dataset rows for this crop (e.g. a vegetable that isn't in
            # the fruit price dataset). Reuse the single shared all-crops
            # model instead of training a brand new one for every distinct
            # crop name that misses - that was causing many full-dataset
            # RandomForest trainings to run at once and time out callers.
            if model_name == 'all':
                raise
            result = load_model(crop=None)

        _MODEL_CACHE[model_name] = result
        return result


def predict_price(district, planting_date, crop=None):
    model, _ = load_model(crop=crop)
    planting = pd.to_datetime(planting_date)
    features = {
        'district': district,
        'month': planting.month,
        'day_of_year': planting.dayofyear,
        'temperature': 30.0,
        'rainfall': 100.0,
        'humidity': 75.0,
    }

    X = pd.DataFrame([features])
    X = pd.get_dummies(X, columns=['district', 'month'], drop_first=True)
    df_train = load_data()
    if 'rainfall' not in df_train.columns and 'rainfall_mm' in df_train.columns:
        df_train['rainfall'] = df_train['rainfall_mm']
    if crop:
        crop_df = df_train[df_train['fruit_Commodity'].astype(str).str.lower() == str(crop).strip().lower()]
        if crop_df.empty:
            crop_df = df_train
    else:
        crop_df = df_train
    train_cols = pd.get_dummies(crop_df[['district', 'month', 'day_of_year', 'temperature', 'rainfall', 'humidity']], columns=['district', 'month'], drop_first=True).columns
    for col in train_cols:
        if col not in X.columns:
            X[col] = 0
    X = X[train_cols]
    return float(model.predict(X)[0])


def predict_rainfall(district, planting_date, harvest_date):
    df = load_data()
    district_df = df[df['district'].str.lower() == str(district).strip().lower()]
    if district_df.empty:
        return 0.0

    monthly_means = district_df.groupby('month')['rainfall'].mean().sort_index()
    fallback_mean = float(monthly_means.mean()) if not monthly_means.empty else 0.0

    planting = pd.to_datetime(planting_date)
    harvest = pd.to_datetime(harvest_date)
    total_rainfall = 0.0
    cursor = planting

    while cursor <= harvest:
        month_mean = float(monthly_means.get(cursor.month, fallback_mean))
        total_rainfall += month_mean
        cursor = cursor + pd.DateOffset(months=1)

    return round(max(0.0, total_rainfall), 1)


def get_crop_info(crop=None, harvest_days=None, harvest_type=None, soil_types=None):
    return {
        'crop': crop,
        'harvestType': harvest_type or 'short',
        'harvestDays': harvest_days or 120,
        'soilTypes': soil_types or [],
    }


def get_crop_price_mean(district, crop):
    df = load_data()
    crop_df = df[(df['district'].str.lower() == str(district).strip().lower()) & (df['fruit_Commodity'].astype(str).str.lower() == str(crop).strip().lower())]
    if crop_df.empty:
        return None
    return float(crop_df['price'].mean())
