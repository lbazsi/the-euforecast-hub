from fastapi import APIRouter
from app.services.killchain_service import run_killchain

router = APIRouter()

@router.post("/run")
def killchain_endpoint():
    """Run kill-chain-based forecasting."""
    return run_killchain()
