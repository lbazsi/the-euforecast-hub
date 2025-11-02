from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone
import uuid

from app.core.database import get_session
from app.models.builder import BuilderProject, BuilderMessage
from app.schemas.builder import (
    BuilderProjectCreate,
    BuilderRunRequest,
    BuilderRunResponse,
    BuilderMessageRequest,
    BuilderMessageResponse,
)
from app.services.llama_client import get_llama_forecast
from app.services.dbn_engine import build_spec, fit_model, infer, FIXED_STAGES
from app.utils.responses import error_response

router = APIRouter()

@router.post("/builder/projects", status_code=201)
async def save_project(payload: BuilderProjectCreate, session: AsyncSession = Depends(get_session)):
    stage_configurations = {
        stage: cfg.model_dump(mode="json") if hasattr(cfg, "model_dump") else cfg
        for stage, cfg in payload.stageConfigurations.items()
    }
    rec = BuilderProject(name=payload.name, stage_configurations=stage_configurations)
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
    stage_configs: dict = {}
    if payload.projectId:
        rec = await session.get(BuilderProject, payload.projectId)
        if not rec:
            error_response("NOT_FOUND", "Project not found", 404)
        stage_configs = rec.stage_configurations or {}
    if not stage_configs and payload.stageConfigurations:
        stage_configs = {
            stage: cfg.model_dump(mode="json") if hasattr(cfg, "model_dump") else cfg
            for stage, cfg in payload.stageConfigurations.items()
        }
    if not stage_configs:
        error_response("BAD_REQUEST", "Provide projectId or stageConfigurations", 400)

    scenario_prompt = payload.scenarioPrompt
    if not scenario_prompt and payload.projectId:
        res = await session.execute(
            select(BuilderMessage)
            .where(BuilderMessage.project_id == payload.projectId, BuilderMessage.type == "user")
            .order_by(desc(BuilderMessage.timestamp))
            .limit(1)
        )
        latest_msg = res.scalars().first()
        if latest_msg:
            scenario_prompt = latest_msg.message
    if not scenario_prompt:
        scenario_prompt = "Generate a forecast based on the configured scenario."

    # Call LLaMA to obtain a DBN-ready structure
    llama_json = await get_llama_forecast(scenario_prompt, stage_configs)

    # Persist and process through the DBN engine
    spec_id, structural_warnings = await build_spec(session, llama_json, {"stage_configurations": stage_configs})

    synthetic_rows = []
    for edge in llama_json.get("edges", [])[:5]:
        source_key = f"{edge.get('source')}@0"
        target_key = f"{edge.get('target')}@1"
        synthetic_rows.append({source_key: 1, target_key: 1})
    if not synthetic_rows:
        synthetic_rows.append({})

    mv_id, fit_metrics = await fit_model(
        session,
        spec_id,
        {"synthetic_case": synthetic_rows},
        {"synthetic_case": 1.0},
    )

    stage_posteriors, aggregates = await infer(session, mv_id, evidence={}, interventions={})
    stage_posteriors = {stage: {d: float(v) for d, v in dom.items()} for stage, dom in stage_posteriors.items()}
    aggregates = {d: float(v) for d, v in aggregates.items()}

    timeline = []
    for idx, stage in enumerate(FIXED_STAGES, start=1):
        dom_scores = stage_posteriors.get(stage, {})
        if not dom_scores:
            continue
        top_domain, top_score = max(dom_scores.items(), key=lambda item: item[1])
        timeline.append({
            "t": idx,
            "stage": stage,
            "domain": top_domain,
            "impact": round(top_score, 4),
        })

    scenario_results = {
        "graph": {
            "nodes": llama_json.get("nodes", []),
            "edges": llama_json.get("edges", []),
            "warnings": structural_warnings,
        },
        "timeline": timeline,
        "stagePosteriors": stage_posteriors,
        "aggregateImpacts": aggregates,
    }

    created_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "stagesAnalyzed": FIXED_STAGES,
        "domainWeightsApplied": stage_configs,
        "timestamp": created_at,
        "modelSpecId": spec_id,
        "modelVersionId": mv_id,
        "fitMetrics": fit_metrics,
    }

    return {
        "success": True,
        "data": {
            "forecastId": str(uuid.uuid4()),
            "scenarioResults": scenario_results,
            "metadata": metadata,
            "createdAt": created_at,
        },
    }

@router.post("/builder/message")
async def builder_message(payload: BuilderMessageRequest, session: AsyncSession = Depends(get_session)):
    # Non-conversational MVP: we still return a static response & suggestions keyed to stage configs
    session_id = payload.sessionId or str(uuid.uuid4())
    response = "Your scenario was received. Run the forecast to generate visuals."
    suggestions = ["Run forecast", "Adjust domain weights", "Add a stage-specific NL rule"]
    # Optionally store message if projectId exists
    if payload.projectId:
        msg = BuilderMessage(
            project_id=payload.projectId,
            timestamp=datetime.utcnow().isoformat(),
            message=payload.message,
            type="user",
        )
        session.add(msg)
        await session.commit()
    return {"success": True, "data": {"response": response, "suggestions": suggestions, "sessionId": session_id}}