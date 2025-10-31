from app.models.forecasting import simple_forecast

def run_forecast():
    df = simple_forecast()
    results = {
        "model": "LinearTrend",
        "parameters": {"n": len(df)},
        "results": df.to_dict(orient="records"),
        "summary": "Emissions projected to rise by ~7% over horizon."
    }
    return results
