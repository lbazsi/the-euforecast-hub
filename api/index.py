"""
Vercel serverless function handler for FastAPI app.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import create_app

# Create FastAPI app
app = create_app()

# Export handler for Vercel
# Vercel expects 'handler' variable
handler = app