from pydantic import BaseModel, Field, confloat, conint, constr, field_validator
from typing import Dict, Literal, List, Optional
from datetime import datetime

StageName = Literal["Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"]

class DomainWeights(BaseModel):
    environment: conint(ge=0, le=100)
    economy: conint(ge=0, le=100)
    society: conint(ge=0, le=100)
    policy: conint(ge=0, le=100)
    technology: conint(ge=0, le=100)

    @field_validator("technology")
    @classmethod
    def validate_sum(cls, v, values):
        if len(values) == 4:
            total = v + sum(values.values())
            if total != 100:
                raise ValueError("domainWeights must sum to 100")
        return v

class StageConfig(BaseModel):
    domainWeights: DomainWeights
    nlRuleInput: constr(max_length=2000) | None = None
    importance: confloat(ge=0, le=1) = 0.5

class MessageItem(BaseModel):
    timestamp: str
    message: str
    type: Literal["user","system"]

class BuilderProjectCreate(BaseModel):
    name: constr(min_length=3, max_length=200)
    stageConfigurations: Dict[StageName, StageConfig]
    messageHistory: List[MessageItem] | None = None

class BuilderProjectDetail(BaseModel):
    id: str
    name: str
    stageConfigurations: Dict[str, dict]
    messageHistory: List[MessageItem] | None = None
    createdAt: str
    updatedAt: str

class BuilderRunRequest(BaseModel):
    projectId: Optional[str] = None
    stageConfigurations: Optional[Dict[StageName, StageConfig]] = None
    scenarioPrompt: Optional[str] = None

class BuilderRunResponse(BaseModel):
    forecastId: str
    scenarioResults: dict
    metadata: dict
    createdAt: str

class BuilderMessageRequest(BaseModel):
    message: str
    stageConfigurations: Dict[StageName, StageConfig]
    projectId: Optional[str] = None
    sessionId: Optional[str] = None

class BuilderMessageResponse(BaseModel):
    response: str
    suggestions: list[str]
    sessionId: str
