import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service.model_service import predict_price, predict_rainfall, get_crop_info, get_crop_price_mean

app = FastAPI(title='Smart Crop ML Service')

class RecommendRequest(BaseModel):
    district: str
    crop: str
    plantingDate: str
    language: str = 'en'
    harvestDays: int | None = None
    harvestType: str | None = None
    soilTypes: list[str] | None = None

class RecommendResponse(BaseModel):
    crop: str
    predictedPriceLkr: float
    harvestDate: str
    harvestType: str
    predictedRainfallMm: float
    rainfallRange: str
    suitableSoilTypes: list[str]
    historicalMeanPrice: float | None = None
    profitAboveMean: bool

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
        predicted_price = predict_price(recommend.district, recommend.plantingDate, crop=recommend.crop)
        predicted_rainfall = predict_rainfall(recommend.district, recommend.plantingDate, harvest_date)
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
