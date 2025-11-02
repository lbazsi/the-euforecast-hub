from pydantic import BaseModel, Field, constr
from typing import Dict, Any, Optional

class DBNBuildRequest(BaseModel):
    spec: Dict[str, Any]
    settings: Dict[str, Any] = {}

class DBNBuildResponse(BaseModel):
    model_spec_id: str
    structural_warnings: list[str] = []

class DBNFitRequest(BaseModel):
    model_spec_id: str
    data_bindings: Dict[str, Any] = {}
    weights: Dict[str, float] = {"HIST": 1.0, "PSEUDO": 0.2}

class DBNFitResponse(BaseModel):
    model_version_id: str
    fit_metrics: Dict[str, Any]

class DBNInferRequest(BaseModel):
    model_version_id: str
    evidence: Dict[str, Any] = {}
    interventions: Dict[str, Any] = {}

class DBNInferResponse(BaseModel):
    stage_posteriors: Dict[str, Any]
    aggregates: Dict[str, float]
