from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid

from app.core.database import get_session
from app.models.builder import BuilderProject, BuilderMessage
from app.schemas.builder import (
    BuilderProjectCreate, BuilderProjectDetail,
    BuilderRunRequest, BuilderRunResponse,
    BuilderMessageRequest, BuilderMessageResponse
)
from app.services.llama_client import get_llama_forecast
from app.utils.responses import error_response

router = APIRouter()

@router.post("/builder/projects", status_code=201)
async def save_project(payload: BuilderProjectCreate, session: AsyncSession = Depends(get_session)):
    rec = BuilderProject(name=payload.name, stage_configurations=payload.stageConfigurations)
    session.add(rec)
    await session.commit()
    await session.refresh(rec)

    # message history (optional)
    if payload.messageHistory:
        for m in payload.messageHistory:
            msg = BuilderMessage(project_id=rec.id, timestamp=m.timestamp, message=m.message, type=m.type)
            session.add(msg)
        await session.commit()

    return {"success": True, "data": {"projectId": rec.id, "message": "Project saved successfully"}}

@router.get("/builder/projects/{id}")
async def get_project(id: str, session: AsyncSession = Depends(get_session)):
    rec = await session.get(BuilderProject, id)
    if not rec: error_response("NOT_FOUND", "Project not found", 404)
    # load messages
    msgs = (await session.execute(select(BuilderMessage).where(BuilderMessage.project_id == rec.id))).scalars().all()
    return {"success": True, "data": {
        "id": rec.id,
        "name": rec.name,
        "stageConfigurations": rec.stage_configurations,
        "messageHistory": [{"timestamp": m.timestamp, "message": m.message, "type": m.type} for m in msgs],
        "createdAt": rec.created_at.isoformat(),
        "updatedAt": rec.updated_at.isoformat()
    }}

@router.post("/builder/run")
async def run_builder(payload: BuilderRunRequest, session: AsyncSession = Depends(get_session)):
    stage_configs = {}
    if payload.projectId:
        rec = await session.get(BuilderProject, payload.projectId)
        if not rec: error_response("NOT_FOUND", "Project not found", 404)
        stage_configs = rec.stage_configurations
    elif payload.stageConfigurations:
        stage_configs = payload.stageConfigurations
    else:
        error_response("BAD_REQUEST", "Provide projectId or stageConfigurations", 400)

    # Call LLaMA for skeleton
    llama_json = await get_llama_forecast("Generate forecast skeleton", stage_configs)

    # Compose scenario results per spec (graph + timeline mock)
    scenario_results = {
        "graph": llama_json,
        "timeline": [{"t": i+1, "domain": d, "impact": v} for i,(d,v) in enumerate([
            ("Environment", 0.4), ("Economy", 0.5), ("Society", 0.3)
        ])]
    }

    created_at = datetime.now(timezone.utc).isoformat()
    return {"success": True, "data": {
        "forecastId": str(uuid.uuid4()),
        "scenarioResults": scenario_results,
        "metadata": {"stagesAnalyzed": [
            "Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"
        ], "domainWeightsApplied": stage_configs, "timestamp": created_at},
        "createdAt": created_at
    }}

@router.post("/builder/message")
async def builder_message(payload: BuilderMessageRequest, session: AsyncSession = Depends(get_session)):
    # Non-conversational MVP: we still return a static response & suggestions keyed to stage configs
    session_id = payload.sessionId or str(uuid.uuid4())
    response = "Your scenario was received. Run the forecast to generate visuals."
    suggestions = ["Run forecast", "Adjust domain weights", "Add a stage-specific NL rule"]
    # Optionally store message if projectId exists
    if payload.projectId:
        msg = BuilderMessage(project_id=payload.projectId, timestamp=datetime.utcnow().isoformat(), message=payload.message, type="user")
        session.add(msg); await session.commit()
    return {"success": True, "data": {"response": response, "suggestions": suggestions, "sessionId": session_id}}
