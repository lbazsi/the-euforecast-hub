import numpy as np
import pandas as pd

def simple_forecast(n=36):
    """Simple linear forecast for demo."""
    t = np.arange(n)
    values = 100 + 0.5 * t + np.random.normal(0, 1, n)
    df = pd.DataFrame({"time": list(range(n)), "values": values})
    return df
