"""
Vercel serverless function handler for FastAPI app.
Vercel supports ASGI apps directly, so we export the FastAPI app.
"""
from app.main import create_app
from app.core.database import init_models

# Create FastAPI app
app = create_app()

# Initialize database models on app startup
@app.on_event("startup")
async def startup_event():
    """Initialize database models when the app starts."""
    try:
        await init_models()
        print("Database models initialized successfully")
    except Exception as e:
        # Log error but don't fail - connection will be retried on first request
        print(f"Warning: Database initialization failed: {e}")
        print("Database will be initialized on first request.")

# Export app for Vercel
# Vercel's Python runtime will handle ASGI apps directly
handler = app
