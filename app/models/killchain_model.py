def killchain_simulation(initial_prob=0.8):
    """Simple kill-chain simulation based on sequential probability decay."""
    stages = [
        {"name": "Observation", "prob": round(initial_prob, 2)},
        {"name": "Characterization", "prob": round(initial_prob * 0.9, 2)},
        {"name": "Decision", "prob": round(initial_prob * 0.7, 2)},
        {"name": "Impact", "prob": round(initial_prob * 0.55, 2)},
        {"name": "Mitigation", "prob": round(initial_prob * 0.45, 2)}
    ]
    overall = stages[-1]["prob"]
    return stages, overall
