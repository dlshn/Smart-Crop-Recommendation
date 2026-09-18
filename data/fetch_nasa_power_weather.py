"""One-off script: replaces the synthetic Temperature/Rainfall/Humidity
columns in dataset.csv with real daily weather from the NASA POWER API
(satellite/reanalysis data, free, no API key), matched per district by
its approximate centroid coordinates. Crop/price columns are left
untouched -- only the weather columns are swapped for real data, so the
Prophet forecasting models train on an actual seasonal signal instead of
noise.

Run once: python fetch_nasa_power_weather.py
"""
import io
import os
import time
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset.csv')
BACKUP_PATH = os.path.join(BASE_DIR, 'dataset_synthetic_backup.csv')

START_DATE = '20200101'
END_DATE = '20241231'

# Approximate district-capital coordinates (lat, lon)
DISTRICT_COORDS = {
    'Ampara': (7.2975, 81.6747),
    'Anuradhapura': (8.3114, 80.4037),
    'Badulla': (6.9895, 81.0567),
    'Batticaloa': (7.7170, 81.7000),
    'Colombo': (6.9271, 79.8612),
    'Galle': (6.0535, 80.2210),
    'Gampaha': (7.0917, 79.9999),
    'Hambantota': (6.1246, 81.1185),
    'Jaffna': (9.6615, 80.0255),
    'Kalutara': (6.5854, 79.9607),
    'Kandy': (7.2906, 80.6337),
    'Kegalle': (7.2513, 80.3464),
    'Kilinochchi': (9.3803, 80.3770),
    'Kurunegala': (7.4818, 80.3609),
    'Mannar': (8.9810, 79.9044),
    'Matale': (7.4675, 80.6234),
    'Matara': (5.9549, 80.5540),
    'Monaragala': (6.8728, 81.3507),
    'Mullaitivu': (9.2670, 80.8142),
    'Nuwara Eliya': (6.9497, 80.7891),
    'Polonnaruwa': (7.9403, 81.0188),
    'Puttalam': (8.0362, 79.8283),
    'Ratnapura': (6.6828, 80.4126),
    'Trincomalee': (8.5874, 81.2152),
    'Vavuniya': (8.7514, 80.4971),
}

POWER_URL = 'https://power.larc.nasa.gov/api/temporal/daily/point'


def fetch_district_weather(district, lat, lon):
    params = {
        'parameters': 'PRECTOTCORR,T2M,RH2M',
        'community': 'AG',
        'longitude': lon,
        'latitude': lat,
        'start': START_DATE,
        'end': END_DATE,
        'format': 'JSON',
    }
    resp = requests.get(POWER_URL, params=params, timeout=60)
    resp.raise_for_status()
    payload = resp.json()['properties']['parameter']

    dates = sorted(payload['PRECTOTCORR'].keys())
    rows = []
    for d in dates:
        rows.append({
            'Date': pd.to_datetime(d, format='%Y%m%d'),
            'Region': district,
            'Temperature': payload['T2M'][d],
            'Rainfall': payload['PRECTOTCORR'][d],
            'Humidity': payload['RH2M'][d],
        })
    return pd.DataFrame(rows)


def main():
    print(f'Reading existing dataset: {DATASET_PATH}')
    original = pd.read_csv(DATASET_PATH, encoding='latin1', low_memory=False)
    original.columns = [c.strip() for c in original.columns]
    original['Date'] = pd.to_datetime(original['Date'])
    original['Region'] = original['Region'].str.strip()

    if not os.path.exists(BACKUP_PATH):
        original.to_csv(BACKUP_PATH, index=False)
        print(f'Backed up original (synthetic weather) dataset to {BACKUP_PATH}')

    weather_frames = []
    for i, (district, (lat, lon)) in enumerate(DISTRICT_COORDS.items(), 1):
        print(f'[{i}/{len(DISTRICT_COORDS)}] Fetching NASA POWER data for {district} ({lat}, {lon})...')
        weather_frames.append(fetch_district_weather(district, lat, lon))
        time.sleep(0.5)  # be polite to the free API

    real_weather = pd.concat(weather_frames, ignore_index=True)
    print(f'Fetched {len(real_weather)} real (district, date) weather rows.')

    temp_col = [c for c in original.columns if 'Temperature' in c][0]
    rain_col = [c for c in original.columns if 'Rainfall' in c][0]
    hum_col = [c for c in original.columns if 'Humidity' in c][0]

    merged = original.merge(real_weather, on=['Date', 'Region'], how='left')
    missing = merged['Rainfall'].isna().sum()
    if missing:
        print(f'WARNING: {missing} rows had no matching NASA POWER data (kept original synthetic values for those).')
        merged[temp_col] = merged['Temperature'].fillna(merged[temp_col])
        merged[rain_col] = merged['Rainfall'].fillna(merged[rain_col])
        merged[hum_col] = merged['Humidity'].fillna(merged[hum_col])
    else:
        merged[temp_col] = merged['Temperature']
        merged[rain_col] = merged['Rainfall']
        merged[hum_col] = merged['Humidity']

    merged = merged.drop(columns=['Temperature', 'Rainfall', 'Humidity'])
    merged.to_csv(DATASET_PATH, index=False)
    print(f'Wrote real weather data into {DATASET_PATH}')


if __name__ == '__main__':
    main()
