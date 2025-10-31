from fastapi import APIRouter
from app.services.forecast_service import run_forecast

router = APIRouter()

@router.post("/run")
def forecast_endpoint():
    """Run basic forecasting model."""
    return run_forecast()

