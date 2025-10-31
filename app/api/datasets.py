from fastapi import APIRouter
from app.services.data_service import list_datasets, load_sample_data

router = APIRouter()

@router.get("/list")
def dataset_list():
    """List available datasets."""
    return list_datasets()

@router.get("/sample")
def sample_dataset():
    """Return a preview of sample dataset."""
    return load_sample_data()
