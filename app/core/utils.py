import pandas as pd

def read_csv(filepath):
    """Safely read CSV into DataFrame."""
    try:
        df = pd.read_csv(filepath)
        return df.head(10).to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
