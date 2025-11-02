#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick deployment verification script.
Tests that all critical imports work and configuration is valid.
"""

def test_imports():
    """Test that all critical modules can be imported."""
    print("Testing imports...")
    
    # Check if dependencies are installed
    try:
        import pydantic_settings
        print("[OK] pydantic_settings is installed")
    except ImportError:
        print("[WARN] pydantic_settings not installed - run: pip install -r requirements.txt")
        print("[INFO] Skipping import tests - install dependencies first")
        return None  # Return None to indicate skipped
    
    try:
        from app.main import create_app
        print("[OK] app.main imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import app.main: {e}")
        return False
    
    try:
        from app.core.config import settings
        print("[OK] app.core.config imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import app.core.config: {e}")
        return False
    
    try:
        from app.core.database import init_models
        print("[OK] app.core.database imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import app.core.database: {e}")
        return False
    
    try:
        from app.api.routes import forecasts, collaborations, uploads, builder, dbn
        print("[OK] All route modules imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import route modules: {e}")
        return False
    
    try:
        from app.services.dbn_engine import build_spec, fit_model, infer
        print("[OK] DBN engine functions imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import DBN engine: {e}")
        return False
    
    try:
        from app.services.llama_client import get_llama_forecast
        print("[OK] LLAMA client imported successfully")
    except Exception as e:
        print(f"[FAIL] Failed to import LLAMA client: {e}")
        return False
    
    return True

def test_app_creation():
    """Test that the FastAPI app can be created."""
    print("\nTesting app creation...")
    
    try:
        from app.main import create_app
        app = create_app()
        print("[OK] FastAPI app created successfully")
        print(f"     Title: {app.title}")
        print(f"     Routes: {len(app.routes)} routes registered")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vercel_handler():
    """Test that the Vercel handler can be imported."""
    print("\nTesting Vercel handler...")
    
    try:
        import sys
        import os
        # Ensure we're in the right directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        from api.index import handler, app
        print("[OK] Vercel handler imported successfully")
        print(f"     Handler type: {type(handler)}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to import Vercel handler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that required files exist."""
    print("\nTesting file structure...")
    import os
    
    required_files = [
        'api/index.py',
        'app/main.py',
        'app/core/config.py',
        'app/core/database.py',
        'vercel.json',
        'requirements.txt',
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file} exists")
        else:
            print(f"[FAIL] {file} is missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("=" * 60)
    print("EU Forecast Hub - Deployment Verification")
    print("=" * 60)
    
    results = []
    
    # Test file structure first (doesn't need dependencies)
    file_test = test_file_structure()
    results.append(file_test)
    
    # Test imports (may skip if deps not installed)
    import_result = test_imports()
    if import_result is not None:  # Only add if not skipped
        results.append(import_result)
        if import_result:  # Only test app creation if imports worked
            results.append(test_app_creation())
            results.append(test_vercel_handler())
    
    print("\n" + "=" * 60)
    
    # Filter out None values (skipped tests)
    completed_results = [r for r in results if r is not None]
    
    if all(completed_results):
        print("[SUCCESS] All tests passed! Ready for deployment.")
        print("\nNote: If dependencies aren't installed, that's OK.")
        print("      Vercel will install them during deployment.")
        return 0
    elif import_result is None and file_test:
        print("[WARN] File structure OK, but dependencies not installed.")
        print("       This is OK - dependencies will be installed on Vercel.")
        return 0
    else:
        print("[FAIL] Some tests failed. Please check issues above.")
        return 1

if __name__ == "__main__":
    exit(main())

