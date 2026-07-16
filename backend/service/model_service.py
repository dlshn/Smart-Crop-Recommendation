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
    """Loads dataset.csv and reshapes it into a long format with one row
    per (date, district, crop) -- covering BOTH fruit and vegetable
    commodities. The raw file has separate fruit_Commodity/fruit_Price
    and vegitable_Commodity/vegitable_Price column pairs on the same row
    (both sharing the same Date/Region/Temperature/Rainfall/Humidity);
    melting them into a single crop/price pair means every crop --
    fruit or vegetable -- gets its own real price history instead of
    vegetables silently falling back to fruit-only data.
    """
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE

    # read with latin1 to be tolerant of degree symbol encodings
    raw = pd.read_csv(DATA_PATH, encoding='latin1', low_memory=False)
    raw['Date'] = pd.to_datetime(raw['Date'], errors='coerce')
    raw = raw.dropna(subset=['Date', 'Region'])
    raw['district'] = raw['Region'].str.strip()
    raw['month'] = raw['Date'].dt.month
    raw['day_of_year'] = raw['Date'].dt.dayofyear

    # Robust column detection: headers may include odd characters for ° (degree)
    def find_col(cols, keywords):
        for k in keywords:
            for c in cols:
                if k.lower() in c.lower():
                    return c
        return None

    cols = raw.columns.tolist()
    temp_col = find_col(cols, ['temperature', 'temp', '°c', 'c)'])
    rain_col = find_col(cols, ['rainfall', 'rain'])
    hum_col = find_col(cols, ['humidity', 'humid'])
    fruit_crop_col = find_col(cols, ['fruit_commodity', 'fruit commodity'])
    fruit_price_col = find_col(cols, ['fruit_price', 'fruit price'])
    veg_crop_col = find_col(cols, ['vegitable_commodity', 'vegetable_commodity', 'vegitable commodity', 'vegetable commodity'])
    veg_price_col = find_col(cols, ['vegitable_price', 'vegetable_price', 'vegitable price', 'vegetable price'])

    if temp_col is None or rain_col is None or hum_col is None:
        raise RuntimeError(f"Required weather columns not found. Detected columns: {cols}")
    if fruit_crop_col is None or fruit_price_col is None:
        raise RuntimeError(f"Fruit commodity/price columns not found. Detected columns: {cols}")

    raw['temperature'] = pd.to_numeric(raw[temp_col], errors='coerce')
    raw['rainfall'] = pd.to_numeric(raw[rain_col], errors='coerce')
    raw['humidity'] = pd.to_numeric(raw[hum_col], errors='coerce')

    shared_cols = ['district', 'month', 'day_of_year', 'temperature', 'rainfall', 'humidity']

    fruit_part = raw[shared_cols + [fruit_crop_col, fruit_price_col]].rename(
        columns={fruit_crop_col: 'crop', fruit_price_col: 'price'}
    )

    parts = [fruit_part]

    if veg_crop_col is not None and veg_price_col is not None:
        veg_part = raw[shared_cols + [veg_crop_col, veg_price_col]].rename(
            columns={veg_crop_col: 'crop', veg_price_col: 'price'}
        )
        parts.append(veg_part)
    else:
        print(
            'WARNING: vegetable commodity/price columns not found in dataset.csv -- '
            'vegetable crops will have no real price history and will fall back to '
            'the shared all-crops (fruit-only) model. Detected columns:', cols
        )

    long_df = pd.concat(parts, ignore_index=True)
    long_df['crop'] = long_df['crop'].astype(str).str.strip()
    long_df['price'] = pd.to_numeric(long_df['price'], errors='coerce')

    _DATA_CACHE = long_df.dropna(subset=['temperature', 'rainfall', 'humidity', 'price', 'crop'])
    return _DATA_CACHE


def train_price_model(crop=None):
    df = load_data()

    if crop:
        df = df[df['crop'].str.lower() == str(crop).strip().lower()]
    # else: keep all rows (all crops) for the shared fallback model

    if df.empty:
        raise RuntimeError(f'No data found for crop: {crop}')

    df = df.copy()
    df['price'] = df['price'].fillna(df['price'].median())

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
            # No dataset rows for this crop. Reuse the single shared
            # all-crops model instead of training a brand new one for
            # every distinct crop name that misses.
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
    if crop:
        crop_df = df_train[df_train['crop'].str.lower() == str(crop).strip().lower()]
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
    """Returns this crop's OWN historical average price in this district
    -- a distinct, individually-computed value per crop (not a single
    shared value reused across all crops). Used by app.py to decide
    whether a crop's predicted future price is above its own normal
    baseline."""
    df = load_data()
    crop_df = df[
        (df['district'].str.lower() == str(district).strip().lower()) &
        (df['crop'].str.lower() == str(crop).strip().lower())
    ]
    if crop_df.empty:
        return None
    return float(crop_df['price'].mean())
