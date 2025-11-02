from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import forecasts, collaborations, uploads, builder, dbn

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="0.1.0")

    # CORS - ensure CORS_ORIGINS is a list
    cors_origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.API_PREFIX
    app.include_router(forecasts.router, prefix=prefix, tags=["Forecasts"])
    app.include_router(collaborations.router, prefix=prefix, tags=["Collaborations"])
    app.include_router(uploads.router, prefix=prefix, tags=["Uploads"])
    app.include_router(builder.router, prefix=prefix, tags=["Builder"])
    app.include_router(dbn.router, prefix=prefix, tags=["DBN"])

    @app.get("/", include_in_schema=False)
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "message": "EU Forecast Hub API",
                "docs_url": "https://the-euforecast-hub.vercel.app/docs",
                "healthcheck": f"{prefix}/health",
            }
        )

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> Response:
        return Response(status_code=204)

    @app.get("/favicon.png", include_in_schema=False)
    async def favicon_png() -> Response:
        return Response(status_code=204)

    @app.get(f"{prefix}/health")
    async def health():
        return {"success": True, "data": {"status": "ok"}}

    return app
    app = create_app()


app = create_app()