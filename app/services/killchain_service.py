from app.models.killchain_model import killchain_simulation

def run_killchain():
    stages, overall = killchain_simulation()
    narrative = f"Overall impact probability: {overall}. Risk propagation modeled through 5 classical kill-chain stages."
    return {
        "chain_id": "KC001",
        "stages": stages,
        "overall_outcome_prob": overall,
        "narrative": narrative
    }
