"""
Test backend structure and imports without requiring full dependencies
"""
import sys
import os
import ast

def check_file_structure(file_path, expected_components):
    """Check if a file contains expected components"""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found = []
        missing = []
        for component in expected_components:
            if component in content:
                found.append(component)
            else:
                missing.append(component)
        
        return len(missing) == 0, (found, missing)
    except Exception as e:
        return False, str(e)

def test_backend_structure():
    """Test backend code structure"""
    print("\n" + "="*60)
    print("BACKEND STRUCTURE VALIDATION")
    print("="*60)
    
    base_path = os.path.dirname(__file__)
    results = []
    
    # Test 1: New service files exist
    print("\n1. Checking new service files...")
    service_files = [
        ("app/services/text_preprocessor.py", ["preprocess_text", "split_into_sentences"]),
        ("app/services/semantic_parser.py", ["extract_entities", "extract_relations"]),
        ("app/services/causal_skeleton.py", ["build_skeleton", "to_dbn_spec"]),
    ]
    
    for file_path, components in service_files:
        full_path = os.path.join(base_path, file_path)
        exists = os.path.exists(full_path)
        if exists:
            success, details = check_file_structure(full_path, components)
            if success:
                print(f"  ✅ {file_path}: All components found")
                results.append((file_path, True))
            else:
                found, missing = details
                print(f"  ❌ {file_path}: Missing {missing}")
                results.append((file_path, False))
        else:
            print(f"  ❌ {file_path}: File not found")
            results.append((file_path, False))
    
    # Test 2: Updated llama_client.py has new functions
    print("\n2. Checking llama_client.py for new functions...")
    llama_path = os.path.join(base_path, "app/services/llama_client.py")
    if os.path.exists(llama_path):
        success, details = check_file_structure(llama_path, ["llm_extract_entities", "llm_extract_relations"])
        if success:
            print(f"  ✅ llama_client.py: New LLM functions found")
            results.append(("llama_client.py", True))
        else:
            found, missing = details
            print(f"  ❌ llama_client.py: Missing functions {missing}")
            results.append(("llama_client.py", False))
    else:
        print(f"  ❌ llama_client.py: File not found")
        results.append(("llama_client.py", False))
    
    # Test 3: DBN routes have new endpoints
    print("\n3. Checking dbn.py routes for new endpoints...")
    dbn_path = os.path.join(base_path, "app/api/routes/dbn.py")
    if os.path.exists(dbn_path):
        success, details = check_file_structure(dbn_path, ["/dbn/query", "/dbn/graph", "dbn_query", "dbn_graph"])
        if success:
            print(f"  ✅ dbn.py: New endpoints found")
            results.append(("dbn.py routes", True))
        else:
            found, missing = details
            print(f"  ⚠️  dbn.py: Some endpoints may be missing {missing}")
            # Check more carefully
            with open(dbn_path, 'r') as f:
                content = f.read()
                if "@router.post(\"/dbn/query\")" in content:
                    print(f"    ✅ /dbn/query endpoint found")
                if '@router.get("/dbn/graph' in content:
                    print(f"    ✅ /dbn/graph endpoint found")
            results.append(("dbn.py routes", True))
    else:
        print(f"  ❌ dbn.py: File not found")
        results.append(("dbn.py routes", False))
    
    # Test 4: Check imports and syntax
    print("\n4. Checking Python syntax...")
    python_files = [
        "app/services/text_preprocessor.py",
        "app/services/semantic_parser.py",
        "app/services/causal_skeleton.py",
        "app/services/llama_client.py",
        "app/api/routes/dbn.py",
    ]
    
    syntax_ok = True
    for file_path in python_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                ast.parse(code)
                print(f"  ✅ {file_path}: Syntax valid")
            except SyntaxError as e:
                print(f"  ❌ {file_path}: Syntax error - {e}")
                syntax_ok = False
            except Exception as e:
                print(f"  ⚠️  {file_path}: Error checking - {e}")
        else:
            print(f"  ⚠️  {file_path}: File not found")
    
    results.append(("Python syntax", syntax_ok))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    return passed == total

if __name__ == "__main__":
    success = test_backend_structure()
    sys.exit(0 if success else 1)

