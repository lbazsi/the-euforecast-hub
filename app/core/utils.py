import pandas as pd

def read_csv(filepath, nrows=10):
    """Safely read a CSV and return a preview."""
    try:
        df = pd.read_csv(filepath, nrows=nrows)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
