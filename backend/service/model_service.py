import os
import threading
import calendar
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# dataset.csv is located at the repository root `data/`, not under backend/service/
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'data', 'dataset.csv')
MODEL_DIR = os.path.join(BASE_DIR, '..', 'models')
WEATHER_MODEL_DIR = os.path.join(MODEL_DIR, 'weather')

FEATURES = ['district', 'month', 'day_of_year', 'temperature', 'rainfall', 'humidity']
WEATHER_VARS = ['temperature', 'rainfall', 'humidity']
# Below this many daily observations, a district's history is too short to
# fit a trustworthy yearly-seasonality curve, so we fall back to a plain
# historical average instead of a Prophet forecast for that district.
MIN_WEATHER_ROWS_FOR_PROPHET = 365 * 2

_DATA_CACHE = None
_MODEL_CACHE = {}
_WEATHER_DATA_CACHE = None
_WEATHER_MODEL_CACHE = {}
_WEATHER_MODEL_LOCK = threading.RLock()


def _find_col(cols, keywords):
    for k in keywords:
        for c in cols:
            if k.lower() in c.lower():
                return c
    return None


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
    cols = raw.columns.tolist()
    temp_col = _find_col(cols, ['temperature', 'temp', '°c', 'c)'])
    rain_col = _find_col(cols, ['rainfall', 'rain'])
    hum_col = _find_col(cols, ['humidity', 'humid'])
    fruit_crop_col = _find_col(cols, ['fruit_commodity', 'fruit commodity'])
    fruit_price_col = _find_col(cols, ['fruit_price', 'fruit price'])
    veg_crop_col = _find_col(cols, ['vegitable_commodity', 'vegetable_commodity', 'vegitable commodity', 'vegetable commodity'])
    veg_price_col = _find_col(cols, ['vegitable_price', 'vegetable_price', 'vegitable price', 'vegitable price'])

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


def load_weather_data():
    """One row per (district, date) with temperature/rainfall/humidity --
    unlike load_data(), rows are NOT exploded per crop. Used to fit
    per-district Prophet forecasting models on the district's real daily
    weather history."""
    global _WEATHER_DATA_CACHE
    if _WEATHER_DATA_CACHE is not None:
        return _WEATHER_DATA_CACHE

    raw = pd.read_csv(DATA_PATH, encoding='latin1', low_memory=False)
    raw['Date'] = pd.to_datetime(raw['Date'], errors='coerce')
    raw = raw.dropna(subset=['Date', 'Region'])
    raw['district'] = raw['Region'].str.strip()

    cols = raw.columns.tolist()
    temp_col = _find_col(cols, ['temperature', 'temp', '°c', 'c)'])
    rain_col = _find_col(cols, ['rainfall', 'rain'])
    hum_col = _find_col(cols, ['humidity', 'humid'])

    raw['temperature'] = pd.to_numeric(raw[temp_col], errors='coerce')
    raw['rainfall'] = pd.to_numeric(raw[rain_col], errors='coerce')
    raw['humidity'] = pd.to_numeric(raw[hum_col], errors='coerce')

    weather = raw[['district', 'Date', 'temperature', 'rainfall', 'humidity']].dropna()
    _WEATHER_DATA_CACHE = weather.drop_duplicates(subset=['district', 'Date'])
    return _WEATHER_DATA_CACHE


def _weather_model_path(district, variable):
    safe_district = str(district).strip().lower().replace(' ', '_')
    return os.path.join(WEATHER_MODEL_DIR, f'{safe_district}_{variable}.json')


def _train_weather_prophet(district, variable):
    district_df = load_weather_data()
    district_df = district_df[district_df['district'].str.lower() == str(district).strip().lower()]
    if len(district_df) < MIN_WEATHER_ROWS_FOR_PROPHET:
        return None

    prophet_df = district_df[['Date', variable]].rename(columns={'Date': 'ds', variable: 'y'}).sort_values('ds')
    # changepoint_prior_scale is lowered from Prophet's default (0.05) because
    # 5 years of noisy daily weather isn't enough history to reliably tell a
    # real long-term trend from day-to-day noise; the default overfits a
    # trend to that noise and extrapolates it into unrealistic (even
    # negative, for rainfall) values a few years out. A near-flat trend
    # leans on the yearly seasonality instead, which the data does support.
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.001,
    )
    model.fit(prophet_df)
    return model


def load_weather_model(district, variable):
    """Loads (training + caching to disk on first use, like load_model())
    the Prophet trend+yearly-seasonality model that forecasts `variable`
    for `district`. Returns None if the district doesn't have enough daily
    history to fit a reliable model."""
    key = (str(district).strip().lower(), variable)
    if key in _WEATHER_MODEL_CACHE:
        return _WEATHER_MODEL_CACHE[key]

    with _WEATHER_MODEL_LOCK:
        if key in _WEATHER_MODEL_CACHE:
            return _WEATHER_MODEL_CACHE[key]

        path = _weather_model_path(district, variable)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    model = model_from_json(f.read())
                _WEATHER_MODEL_CACHE[key] = model
                return model
            except Exception:
                os.remove(path)

        model = _train_weather_prophet(district, variable)
        if model is not None:
            os.makedirs(WEATHER_MODEL_DIR, exist_ok=True)
            with open(path, 'w') as f:
                f.write(model_to_json(model))

        _WEATHER_MODEL_CACHE[key] = model
        return model


def forecast_weather(district, target_date):
    """Forecasts temperature/rainfall/humidity for a specific future date
    using per-district Prophet models (trend + yearly seasonality) fit on
    that district's daily weather history. Returns None when the district
    doesn't have enough history to fit a reliable model, so the caller can
    fall back to a plain historical average."""
    future = pd.DataFrame({'ds': [pd.to_datetime(target_date)]})

    values = {}
    for variable in WEATHER_VARS:
        model = load_weather_model(district, variable)
        if model is None:
            return None
        values[variable] = float(model.predict(future)['yhat'].iloc[0])

    # Prophet's trend+seasonality curve is unbounded and can extrapolate
    # past what's physically possible (e.g. negative rainfall on a
    # historically very dry day/district) -- clamp to valid physical ranges.
    rainfall = max(0.0, values['rainfall'])
    humidity = min(100.0, max(0.0, values['humidity']))

    return values['temperature'], rainfall, humidity


def forecast_rainfall_trend(district, start_date):
    """Prophet-forecasted rainfall (mm) for the 12 calendar months starting
    at start_date (i.e. the planting date's month, which will be a partial
    month if start_date isn't the 1st), each month's total obtained by
    predicting every day in it (matching the mm/day units of the underlying
    weather data) and summing -- the same total-from-daily approach used by
    get_monthly_rainfall_climatology() and predict_rainfall(), so this
    forecast is comparable to those. Real calendar months (28-31 days) are
    used rather than fixed 30-day windows so each of the 12 points maps to
    one distinct, correctly-labelled month with no repeats or gaps. Also
    returns Prophet's confidence interval (summed per month) as an
    approximate uncertainty band. Returns None if the district doesn't have
    enough history to fit Prophet."""
    model = load_weather_model(district, 'rainfall')
    if model is None:
        return None

    windows = []
    cursor = pd.to_datetime(start_date)
    for _ in range(12):
        days_in_month = calendar.monthrange(cursor.year, cursor.month)[1]
        month_end = pd.Timestamp(cursor.year, cursor.month, days_in_month)
        month_days = pd.date_range(cursor, month_end, freq='D')

        forecast = model.predict(pd.DataFrame({'ds': month_days}))
        # Same physical clamp as forecast_weather(): rainfall can't be negative.
        for col in ('yhat', 'yhat_lower', 'yhat_upper'):
            forecast[col] = forecast[col].clip(lower=0.0)

        windows.append({
            'label': cursor.strftime('%b %Y'),
            'rainfall': round(float(forecast['yhat'].sum()), 1),
            'lower': round(float(forecast['yhat_lower'].sum()), 1),
            'upper': round(float(forecast['yhat_upper'].sum()), 1),
        })

        cursor = month_end + pd.Timedelta(days=1)

    return windows


def get_climatology(district, target_date):
    """Weather inputs (temperature, rainfall, humidity) for a future
    prediction -- we obviously don't have real readings for a date that
    hasn't happened yet. Prefers a per-district Prophet forecast, which
    captures long-term trend (e.g. warming) and yearly seasonality instead
    of a flat historical average; falls back to the plain historical
    month-average for districts with too little history to fit Prophet
    reliably."""
    forecasted = forecast_weather(district, target_date)
    if forecasted is not None:
        return forecasted

    target_date = pd.to_datetime(target_date)
    df = load_data()
    district_df = df[df['district'].str.lower() == str(district).strip().lower()]
    if district_df.empty:
        district_df = df

    month_df = district_df[district_df['month'] == target_date.month]
    if month_df.empty:
        month_df = district_df

    means = month_df[['temperature', 'rainfall', 'humidity']].mean()
    return float(means['temperature']), float(means['rainfall']), float(means['humidity'])


def predict_price(district, planting_date, crop=None, harvest_date=None):
    """Predicts the price for the month the crop is actually READY TO
    SELL, not the month it was planted. If harvest_date is not given,
    falls back to planting_date (kept for backward compatibility with
    any other caller), but callers that know the crop's harvestDays
    should always pass harvest_date = planting_date + harvestDays."""
    model, _ = load_model(crop=crop)
    target_date = pd.to_datetime(harvest_date if harvest_date is not None else planting_date)
    temperature, rainfall, humidity = get_climatology(district, target_date)
    features = {
        'district': district,
        'month': target_date.month,
        'day_of_year': target_date.dayofyear,
        'temperature': temperature,
        'rainfall': rainfall,
        'humidity': humidity,
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


def rainfall_breakdown_for_period(district, planting_date, harvest_date):
    """Per-calendar-month rainfall (mm) breakdown covering the growing
    period (planting_date to harvest_date), rounded UP to whole calendar
    months: the first month starts at planting_date (partial, since
    rainfall before planting isn't part of the growing period) but every
    month is otherwise taken in full through its real end-of-month date,
    including the harvest month, even though the crop is harvested partway
    through it. This means a given calendar month always covers the exact
    same date range -- and so gets the exact same forecast -- everywhere
    it's shown (this chart for any crop whose growing period reaches that
    month, and the 12-month forecast_rainfall_trend() chart), rather than
    being cut short at each crop's own harvest date and drifting from one
    crop to another. Every day is forecast individually by the district's
    Prophet rainfall model and summed per month -- the same day-by-day
    approach forecast_rainfall_trend() uses. Falls back to the historical
    daily average (via get_climatology()) for districts without enough
    history to fit Prophet."""
    planting = pd.to_datetime(planting_date)
    harvest = pd.to_datetime(harvest_date)
    model = load_weather_model(district, 'rainfall')

    breakdown = []
    cursor = planting

    while cursor <= harvest:
        days_in_month = calendar.monthrange(cursor.year, cursor.month)[1]
        month_end = pd.Timestamp(cursor.year, cursor.month, days_in_month)
        period_days = pd.date_range(cursor, month_end, freq='D')

        if model is not None:
            forecast = model.predict(pd.DataFrame({'ds': period_days}))
            total = float(forecast['yhat'].clip(lower=0.0).sum())
        else:
            _, daily_rainfall, _ = get_climatology(district, cursor)
            total = daily_rainfall * len(period_days)

        breakdown.append({
            'label': cursor.strftime('%b %Y'),
            'rainfall': round(max(0.0, total), 1),
        })

        cursor = month_end + pd.Timedelta(days=1)

    return breakdown


def predict_rainfall(district, planting_date, harvest_date):
    """Total expected rainfall (mm) over the growing period -- the sum of
    rainfall_breakdown_for_period()'s per-month figures."""
    breakdown = rainfall_breakdown_for_period(district, planting_date, harvest_date)
    total = sum(item['rainfall'] for item in breakdown)
    return round(max(0.0, total), 1)


def get_crop_info(crop=None, harvest_days=None, harvest_type=None, soil_types=None):
    return {
        'crop': crop,
        'harvestType': harvest_type or 'short',
        'harvestDays': harvest_days or 120,
        'soilTypes': soil_types or [],
    }


def _average_monthly_totals(df):
    """Sums the daily rainfall rate (mm/day) within each real (year, month)
    to get that month's actual total, then averages those totals across the
    years in the data -- the "average monthly rainfall" a rainfall-profile
    chart should show, as opposed to an average daily rate."""
    df = df.copy()
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    monthly_totals = df.groupby(['year', 'month'])['rainfall'].sum()
    return monthly_totals.groupby('month').mean()


def get_monthly_rainfall_climatology(district):
    """Average historical TOTAL rainfall (mm) for each of the 12 months in
    this district, e.g. for charting a Jan-Dec rainfall profile. Falls back
    to the countrywide monthly average for any month/district with no rows.
    Uses load_weather_data() (one row per district+date) rather than
    load_data() (exploded per crop) so summing days within a month isn't
    double-counted by the fruit/veg row duplication."""
    df = load_weather_data()
    district_df = df[df['district'].str.lower() == str(district).strip().lower()]
    if district_df.empty:
        district_df = df

    by_month = _average_monthly_totals(district_df)
    fallback_by_month = _average_monthly_totals(df)

    return [
        round(float(by_month.get(m, fallback_by_month.get(m, 0.0))), 1)
        for m in range(1, 13)
    ]


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
