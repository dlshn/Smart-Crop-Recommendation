import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service.model_service import (
    predict_price,
    rainfall_breakdown_for_period,
    get_crop_info,
    get_crop_price_mean,
    get_monthly_rainfall_climatology,
    forecast_rainfall_trend,
)

app = FastAPI(title='Smart Crop ML Service')

class RecommendRequest(BaseModel):
    district: str
    crop: str
    plantingDate: str
    language: str = 'en'
    harvestDays: int | None = None
    harvestType: str | None = None
    soilTypes: list[str] | None = None

class RainfallBreakdownItem(BaseModel):
    label: str
    rainfall: float

class RecommendResponse(BaseModel):
    crop: str
    predictedPriceLkr: float
    harvestDate: str
    harvestType: str
    predictedRainfallMm: float
    rainfallRange: str
    rainfallBreakdown: list[RainfallBreakdownItem]
    suitableSoilTypes: list[str]
    historicalMeanPrice: float | None = None
    profitAboveMean: bool

@app.get('/rainfall-climatology')
def rainfall_climatology(district: str):
    try:
        monthly_mm = get_monthly_rainfall_climatology(district)
        return {'district': district, 'monthlyRainfallMm': monthly_mm}
    except Exception:
        import traceback
        print('Internal error in /rainfall-climatology endpoint:\n', traceback.format_exc())
        raise HTTPException(status_code=500, detail='Internal server error')


@app.get('/rainfall-forecast')
def rainfall_forecast(district: str, plantingDate: str):
    try:
        trend = forecast_rainfall_trend(district, plantingDate)
        if trend is None:
            raise HTTPException(status_code=404, detail=f'Not enough weather history to forecast for {district}')
        return {'district': district, 'plantingDate': plantingDate, 'trend': trend}
    except HTTPException:
        raise
    except Exception:
        import traceback
        print('Internal error in /rainfall-forecast endpoint:\n', traceback.format_exc())
        raise HTTPException(status_code=500, detail='Internal server error')


@app.post('/predict', response_model=RecommendResponse)
def predict(recommend: RecommendRequest):
    try:
        crop_info = get_crop_info(
            crop=recommend.crop,
            harvest_days=recommend.harvestDays,
            harvest_type=recommend.harvestType,
            soil_types=recommend.soilTypes,
        )

        planting_date = datetime.fromisoformat(recommend.plantingDate)
        harvest_date = planting_date + timedelta(days=crop_info['harvestDays'])
        predicted_price = predict_price(recommend.district, recommend.plantingDate, crop=recommend.crop, harvest_date=harvest_date)
        rainfall_breakdown = rainfall_breakdown_for_period(recommend.district, recommend.plantingDate, harvest_date)
        predicted_rainfall = round(sum(item['rainfall'] for item in rainfall_breakdown), 1)
        rainfall_range = 'Low' if predicted_rainfall < 300 else 'Medium' if predicted_rainfall < 600 else 'High'
        historical_mean_price = get_crop_price_mean(recommend.district, recommend.crop)
        profit_above_mean = historical_mean_price is not None and predicted_price > historical_mean_price

        return {
            'crop': recommend.crop,
            'predictedPriceLkr': round(predicted_price, 2),
            'harvestDate': harvest_date.date().isoformat(),
            'harvestType': crop_info['harvestType'],
            'predictedRainfallMm': round(predicted_rainfall, 1),
            'rainfallRange': rainfall_range,
            'rainfallBreakdown': rainfall_breakdown,
            'suitableSoilTypes': crop_info.get('soilTypes', []),
            'historicalMeanPrice': round(historical_mean_price, 2) if historical_mean_price is not None else None,
            'profitAboveMean': profit_above_mean,
        }
    except HTTPException:
        raise
    except Exception:
        import traceback
        tb = traceback.format_exc()
        # Log full traceback to the server console
        print('Internal error in /predict endpoint:\n', tb)
        raise HTTPException(status_code=500, detail='Internal server error')
