from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from sqlalchemy import select, desc
from app.core.database import get_session
from app.schemas.dbn import DBNBuildRequest, DBNFitRequest, DBNInferRequest
from app.services.dbn_engine import build_spec, fit_model, infer
from app.services.text_preprocessor import preprocess_text
from app.services.semantic_parser import extract_entities, extract_relations, score_context
from app.services.causal_skeleton import build_skeleton, to_dbn_spec
from app.utils.responses import error_response
from app.models.dbn import DBNModelSpec, DBNModelVersion

router = APIRouter()

@router.post("/dbn/build")
async def dbn_build(payload: DBNBuildRequest, session: AsyncSession = Depends(get_session)):
    spec_id, warnings = await build_spec(session, payload.spec, payload.settings)
    return {"success": True, "data": {"model_spec_id": spec_id, "structural_warnings": warnings}}

@router.post("/dbn/fit")
async def dbn_fit(payload: DBNFitRequest, session: AsyncSession = Depends(get_session)):
    try:
        mv_id, metrics = await fit_model(session, payload.model_spec_id, payload.data_bindings, payload.weights)
        return {"success": True, "data": {"model_version_id": mv_id, "fit_metrics": metrics}}
    except ValueError as e:
        return error_response("FIT_ERROR", str(e), 400)
    except Exception as e:
        return error_response("FIT_ERROR", f"Failed to fit model: {str(e)}", 500)

@router.post("/dbn/infer")
async def dbn_infer(payload: DBNInferRequest, session: AsyncSession = Depends(get_session)):
    try:
        post, agg = await infer(session, payload.model_version_id, payload.evidence, payload.interventions)
        return {"success": True, "data": {"stage_posteriors": post, "aggregates": agg}}
    except ValueError as e:
        return error_response("INFER_ERROR", str(e), 400)
    except Exception as e:
        return error_response("INFER_ERROR", f"Failed to run inference: {str(e)}", 500)

@router.post("/dbn/query")
async def dbn_query(
    payload: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        raw = payload.get("prompt", "") or ""
        file_id: Optional[str] = payload.get("file_id")
        # Phase 0: preprocess
        sents = await preprocess_text(session, raw_text=raw, file_id=file_id)
        if not sents:
            return error_response("QUERY_ERROR", "No input text found", 400)
        # Phase 1: semantics
        ents = await extract_entities(sents)
        rels = await extract_relations(sents)
        rels = await score_context(rels)
        # Phase 2: skeleton
        skel = build_skeleton(ents, rels)
        spec = to_dbn_spec(skel)
        # Phase 3a: build spec
        spec_id, warnings = await build_spec(session, spec, settings={})
        
        # Phase 3b: fit (using stronger synthetic pseudo-training data)
        edges = spec.get("edges", [])
        if not edges:
            return error_response("QUERY_ERROR", "No causal edges were extracted. Try a more explicit scenario.", 400)
        
        synthetic = []
        # Generate positive and negative examples aligned with source@t → target@t+1
        for e in edges[:4]:
            s, t = e.get("source"), e.get("target")
            if s and t:
                synthetic.append({f"{s}@0": 1, f"{t}@1": 1})  # positive
                synthetic.append({f"{s}@0": 1, f"{t}@1": 1})  # upweight
                synthetic.append({f"{s}@0": 1, f"{t}@1": 0})  # negative
        
        # Add some noise for targets
        for e in edges[1:3]:
            t = e.get("target")
            if t:
                synthetic.append({f"{t}@1": 0})  # noise
        
        data_bindings = {"synthetic_case": synthetic if synthetic else [{}]}
        mv_id, metrics = await fit_model(session, spec_id, data_bindings, weights={"synthetic_case": 1.0})
        # Phase 3c: infer
        post, agg = await infer(session, mv_id, evidence={}, interventions={})
        # Phase 4: packaged response
        return {"success": True, "data": {
            "nodes": spec.get("nodes", []),
            "edges": spec.get("edges", []),
            "stage_posteriors": post,
            "aggregates": agg,
            "fit_metrics": metrics,
            "warnings": warnings
        }}
    except ValueError as e:
        return error_response("QUERY_ERROR", str(e), 400)
    except Exception as e:
        return error_response("QUERY_ERROR", f"Failed to process query: {str(e)}", 500)

@router.get("/dbn/graph/{spec_id}")
async def dbn_graph(spec_id: str, session: AsyncSession = Depends(get_session)):
    try:
        q = await session.get(DBNModelSpec, spec_id)
        if not q:
            return error_response("GRAPH_ERROR", "Spec not found", 404)
        # Get latest version
        res = await session.execute(select(DBNModelVersion).where(DBNModelVersion.spec_id==spec_id).order_by(desc(DBNModelVersion.created_at)))
        mv = res.scalars().first()
        return {"success": True, "data": {
            "spec": q.spec,
            "latest_version_id": mv.id if mv else None,
            "metrics": mv.metrics if mv else {}
        }}
    except Exception as e:
        return error_response("GRAPH_ERROR", f"Failed to fetch graph: {str(e)}", 500)

@router.get("/dbn/latest/{spec_id}")
async def dbn_latest_version(spec_id: str, session: AsyncSession = Depends(get_session)):
    """Get the latest model version for a given spec ID (for debugging)."""
    try:
        q = await session.get(DBNModelSpec, spec_id)
        if not q:
            return error_response("GRAPH_ERROR", "Spec not found", 404)
        # Get latest version
        res = await session.execute(
            select(DBNModelVersion)
            .where(DBNModelVersion.spec_id == spec_id)
            .order_by(desc(DBNModelVersion.created_at))
        )
        mv = res.scalars().first()
        if not mv:
            return error_response("GRAPH_ERROR", "No model versions found for this spec", 404)
        return {"success": True, "data": {
            "spec_id": spec_id,
            "model_version_id": mv.id,
            "created_at": mv.created_at.isoformat() if mv.created_at else None,
            "metrics": mv.metrics or {},
            "params": mv.params or {}
        }}
    except Exception as e:
        return error_response("GRAPH_ERROR", f"Failed to fetch latest version: {str(e)}", 500)
