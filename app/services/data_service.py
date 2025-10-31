import os
from app.core.config import DATA_PATH
from app.core.utils import read_csv

def list_datasets():
    files = [f for f in os.listdir(DATA_PATH) if f.endswith(".csv")]
    return {"datasets": files}

def load_sample_data():
    sample = os.path.join(DATA_PATH, "sample_forecast.csv")
    return read_csv(sample)
