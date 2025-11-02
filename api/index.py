"""
Vercel serverless function handler for FastAPI app.
Vercel supports ASGI apps directly, so we export the FastAPI app.
"""
import sys
import os

# Add the project root to Python path
# Vercel deploys files to /var/task/, so we need to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.main import create_app

# Create FastAPI app
app = create_app()

# Export both handler and app for Vercel compatibility
# Note: Database initialization happens in app/main.py startup event
handler = app