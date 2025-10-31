from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import forecast, killchain, datasets

app = FastAPI(
    title="EUForecast Backend",
    description="Backend API for modular and kill-chain-based forecasting",
    version="0.1.0"
)

# CORS (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(killchain.router, prefix="/killchain", tags=["Kill-Chain"])
app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])

@app.get("/")
def root():
    return {"message": "EUForecast Backend is running 🚀"}
