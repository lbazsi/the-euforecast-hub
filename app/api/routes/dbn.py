from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.dbn import DBNBuildRequest, DBNFitRequest, DBNInferRequest
from app.services.dbn_engine import build_spec, fit_model, infer
from app.utils.responses import error_response

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
        error_response("FIT_ERROR", str(e), 400)
    except Exception as e:
        error_response("FIT_ERROR", f"Failed to fit model: {str(e)}", 500)

@router.post("/dbn/infer")
async def dbn_infer(payload: DBNInferRequest, session: AsyncSession = Depends(get_session)):
    try:
        post, agg = await infer(session, payload.model_version_id, payload.evidence, payload.interventions)
        return {"success": True, "data": {"stage_posteriors": post, "aggregates": agg}}
    except ValueError as e:
        error_response("INFER_ERROR", str(e), 400)
    except Exception as e:
        error_response("INFER_ERROR", f"Failed to run inference: {str(e)}", 500)
