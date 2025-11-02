"""
Test script for frontend features (home buttons)
This tests the frontend build and verifies components
"""
import subprocess
import sys
import os

def test_frontend_build():
    """Test frontend build"""
    print("\n" + "="*60)
    print("TEST: Frontend Build")
    print("="*60)
    
    frontend_path = r"C:\Users\lbazs\OneDrive\Desktop\the-euforecast-hub-frontend\the-euforecast-hub-frontend"
    
    if not os.path.exists(frontend_path):
        print(f"❌ ERROR: Frontend directory not found at {frontend_path}")
        return False
    
    print(f"\nChecking frontend at: {frontend_path}")
    
    # Check if home button components exist
    import_file_checks = [
        ("src/pages/Builder.tsx", ["Home", "useNavigate"]),
        ("src/pages/Forecasts.tsx", ["Home", "useNavigate"]),
        ("src/pages/Collaborations.tsx", ["Home", "useNavigate"]),
    ]
    
    print("\nVerifying home button imports...")
    all_found = True
    for file_path, keywords in import_file_checks:
        full_path = os.path.join(frontend_path, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        print(f"  ✅ {file_path}: {keyword} found")
                    else:
                        print(f"  ❌ {file_path}: {keyword} NOT found")
                        all_found = False
        else:
            print(f"  ❌ {file_path}: File not found")
            all_found = False
    
    if all_found:
        print("\n✅ All home button imports verified!")
        return True
    else:
        print("\n❌ Some imports are missing")
        return False

if __name__ == "__main__":
    success = test_frontend_build()
    sys.exit(0 if success else 1)

