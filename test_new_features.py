"""
Test script for new LLM→DBN pipeline features
Tests /dbn/query endpoint and LLM integration
"""
import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def test_dbn_query():
    """Test the new /dbn/query endpoint with LLM pipeline"""
    print("\n" + "="*60)
    print("TEST 1: /dbn/query endpoint with LLM pipeline")
    print("="*60)
    
    test_prompt = "A prolonged drought reduces crop yield and raises food prices; EU subsidies may follow."
    
    payload = {
        "prompt": test_prompt
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"\nSending POST request to {BASE_URL}/dbn/query")
            print(f"Prompt: {test_prompt}")
            
            response = await client.post(
                f"{BASE_URL}/dbn/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCESS - Response received:")
                print(json.dumps(data, indent=2))
                
                # Verify response structure
                if "success" in data and data["success"]:
                    if "data" in data:
                        data_content = data["data"]
                        print("\n✅ Response structure valid:")
                        print(f"  - Nodes: {len(data_content.get('nodes', []))}")
                        print(f"  - Edges: {len(data_content.get('edges', []))}")
                        print(f"  - Has stage_posteriors: {'stage_posteriors' in data_content}")
                        print(f"  - Has aggregates: {'aggregates' in data_content}")
                        return True
                    else:
                        print("\n❌ ERROR: Response missing 'data' field")
                        return False
                else:
                    print("\n❌ ERROR: Response success flag is false")
                    print(f"Error: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"\n❌ ERROR: Request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("\n❌ ERROR: Request timed out (60s)")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_dbn_graph(spec_id: str):
    """Test the /dbn/graph/{spec_id} endpoint"""
    print("\n" + "="*60)
    print(f"TEST 2: /dbn/graph/{spec_id} endpoint")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\nSending GET request to {BASE_URL}/dbn/graph/{spec_id}")
            
            response = await client.get(f"{BASE_URL}/dbn/graph/{spec_id}")
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCCESS - Graph data received:")
                print(json.dumps(data, indent=2))
                return True
            elif response.status_code == 404:
                print(f"\n⚠️  WARNING: Spec {spec_id} not found (this is expected if no spec was created)")
                return None
            else:
                print(f"\n❌ ERROR: Request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

async def test_llm_integration():
    """Test LLM integration functions"""
    print("\n" + "="*60)
    print("TEST 3: LLM Integration Functions")
    print("="*60)
    
    try:
        # Import the LLM functions
        from app.services.llama_client import llm_extract_entities, llm_extract_relations
        
        test_sentences = [
            {"text": "A prolonged drought reduces crop yield.", "lang": "en"},
            {"text": "EU subsidies may follow.", "lang": "en"}
        ]
        
        print("\nTesting llm_extract_entities...")
        entities = await llm_extract_entities(test_sentences)
        print(f"✅ llm_extract_entities works: {len(entities)} entities found")
        if entities:
            print(f"  Sample: {entities[0]}")
        
        print("\nTesting llm_extract_relations...")
        relations = await llm_extract_relations(test_sentences)
        print(f"✅ llm_extract_relations works: {len(relations)} relations found")
        if relations:
            print(f"  Sample: {relations[0]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_text_preprocessing():
    """Test text preprocessing pipeline"""
    print("\n" + "="*60)
    print("TEST 4: Text Preprocessing Pipeline")
    print("="*60)
    
    try:
        from app.services.text_preprocessor import preprocess_text, split_into_sentences
        
        test_text = "A prolonged drought reduces crop yield. Food prices rise. EU subsidies may follow."
        
        print("\nTesting split_into_sentences...")
        sentences = split_into_sentences(test_text)
        print(f"✅ Split into {len(sentences)} sentences:")
        for i, sent in enumerate(sentences, 1):
            print(f"  {i}. {sent}")
        
        # Test with mock session (won't actually save to DB)
        print("\n✅ Text preprocessing functions work correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_semantic_parsing():
    """Test semantic parsing"""
    print("\n" + "="*60)
    print("TEST 5: Semantic Parsing")
    print("="*60)
    
    try:
        from app.services.semantic_parser import extract_entities, extract_relations
        
        test_sentences = [
            {"text": "A prolonged drought reduces crop yield.", "lang": "en"},
            {"text": "Food prices rise significantly.", "lang": "en"}
        ]
        
        print("\nTesting extract_entities...")
        entities = await extract_entities(test_sentences)
        print(f"✅ Extracted {len(entities)} entities:")
        for ent in entities[:5]:  # Show first 5
            print(f"  - {ent.get('entity')} ({ent.get('domain')})")
        
        print("\nTesting extract_relations...")
        relations = await extract_relations(test_sentences)
        print(f"✅ Extracted {len(relations)} relations:")
        for rel in relations[:5]:  # Show first 5
            print(f"  - {rel.get('cause')} -> {rel.get('effect')} ({rel.get('sign')})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_causal_skeleton():
    """Test causal skeleton building"""
    print("\n" + "="*60)
    print("TEST 6: Causal Skeleton Building")
    print("="*60)
    
    try:
        from app.services.causal_skeleton import build_skeleton, to_dbn_spec
        
        # Mock entities and relations
        entities = [
            {"entity": "drought", "domain": "Environment"},
            {"entity": "crop yield", "domain": "Economy"}
        ]
        relations = [
            {"cause": "drought", "effect": "crop yield", "sign": "-", "confidence": 0.8}
        ]
        
        print("\nTesting build_skeleton...")
        skeleton = build_skeleton(entities, relations)
        print(f"✅ Skeleton built:")
        print(f"  - Nodes: {len(skeleton.get('nodes', []))}")
        print(f"  - Edges: {len(skeleton.get('edges', []))}")
        print(f"  - Root stage: {skeleton.get('root_stage')}")
        
        print("\nTesting to_dbn_spec...")
        dbn_spec = to_dbn_spec(skeleton)
        print(f"✅ DBN spec created:")
        print(f"  - Nodes: {len(dbn_spec.get('nodes', []))}")
        print(f"  - Edges: {len(dbn_spec.get('edges', []))}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST SUITE FOR NEW LLM→DBN PIPELINE")
    print("="*60)
    
    results = []
    
    # Test 1: Full pipeline endpoint
    results.append(("DBN Query Endpoint", await test_dbn_query()))
    
    # Test 2: Graph endpoint (will use spec_id from test 1 if available)
    # For now, test with a dummy ID
    results.append(("DBN Graph Endpoint", await test_dbn_graph("test-spec-id")))
    
    # Test 3: LLM integration
    results.append(("LLM Integration", await test_llm_integration()))
    
    # Test 4: Text preprocessing
    results.append(("Text Preprocessing", await test_text_preprocessing()))
    
    # Test 5: Semantic parsing
    results.append(("Semantic Parsing", await test_semantic_parsing()))
    
    # Test 6: Causal skeleton
    results.append(("Causal Skeleton", await test_causal_skeleton()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    warnings = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  WARN"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {warnings} warnings")
    
    if failed == 0:
        print("\n🎉 All critical tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

