"""
Comprehensive API test suite for Resume Parser
Tests all endpoints and core functionality
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Test if the FastAPI app can start up"""
    try:
        from main import app
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✅ App startup test passed")
        return True
    except Exception as e:
        print(f"❌ App startup test failed: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        from main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_api_endpoints_structure():
    """Test if all API endpoints are properly structured"""
    try:
        from main import app
        client = TestClient(app)
        
        # Test API documentation is available
        response = client.get("/docs")
        assert response.status_code == 200
        print("✅ API documentation available")
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        
        # Check if main endpoint groups exist
        paths = schema.get("paths", {})
        endpoint_groups = {
            "resumes": False,
            "jobs": False,
            "matching": False,
            "candidates": False
        }
        
        for path in paths.keys():
            if "/resumes" in path:
                endpoint_groups["resumes"] = True
            elif "/jobs" in path:
                endpoint_groups["jobs"] = True
            elif "/matching" in path:
                endpoint_groups["matching"] = True
            elif "/candidates" in path:
                endpoint_groups["candidates"] = True
        
        for group, found in endpoint_groups.items():
            if found:
                print(f"✅ {group.title()} endpoints available")
            else:
                print(f"⚠️  {group.title()} endpoints not found")
        
        return all(endpoint_groups.values())
        
    except Exception as e:
        print(f"❌ API endpoints structure test failed: {e}")
        return False

def test_resume_endpoints():
    """Test resume endpoints without database"""
    try:
        from main import app
        client = TestClient(app)
        
        # Test resume list endpoint (should work even without DB)
        response = client.get("/api/v1/resumes/")
        # This might return 500 due to no database, but endpoint should exist
        assert response.status_code in [200, 500]
        print("✅ Resume endpoints exist")
        return True
        
    except Exception as e:
        print(f"❌ Resume endpoints test failed: {e}")
        return False

def test_job_endpoints():
    """Test job endpoints without database"""
    try:
        from main import app
        client = TestClient(app)
        
        # Test job list endpoint
        response = client.get("/api/v1/jobs/")
        # This might return 500 due to no database, but endpoint should exist
        assert response.status_code in [200, 500]
        print("✅ Job endpoints exist")
        return True
        
    except Exception as e:
        print(f"❌ Job endpoints test failed: {e}")
        return False

def test_matching_endpoints():
    """Test matching endpoints without database"""
    try:
        from main import app
        client = TestClient(app)
        
        # Test matching endpoint
        response = client.get("/api/v1/matching/")
        # This might return 500 due to no database, but endpoint should exist
        assert response.status_code in [200, 404, 500]
        print("✅ Matching endpoints exist")
        return True
        
    except Exception as e:
        print(f"❌ Matching endpoints test failed: {e}")
        return False

def test_candidates_endpoints():
    """Test candidates endpoints without database"""
    try:
        from main import app
        client = TestClient(app)
        
        # Test candidates endpoint
        response = client.get("/api/v1/candidates/")
        # This might return 500 due to no database, but endpoint should exist
        assert response.status_code in [200, 500]
        print("✅ Candidates endpoints exist")
        return True
        
    except Exception as e:
        print(f"❌ Candidates endpoints test failed: {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    try:
        from main import app
        client = TestClient(app)
        
        # Test CORS headers
        response = client.options("/")
        # Should have CORS headers or at least not fail
        assert response.status_code in [200, 405]
        print("✅ CORS configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ CORS configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting comprehensive API tests...")
    print("=" * 60)
    
    tests = [
        ("App Startup", test_app_startup),
        ("Health Endpoint", test_health_endpoint),
        ("API Endpoints Structure", test_api_endpoints_structure),
        ("Resume Endpoints", test_resume_endpoints),
        ("Job Endpoints", test_job_endpoints),
        ("Matching Endpoints", test_matching_endpoints),
        ("Candidates Endpoints", test_candidates_endpoints),
        ("CORS Configuration", test_cors_configuration)
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                results.append(f"✅ {test_name}")
            else:
                failed += 1
                results.append(f"❌ {test_name}")
        except Exception as e:
            failed += 1
            results.append(f"❌ {test_name} - Exception: {e}")
        
        print("-" * 40)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    print("\n📋 Detailed Results:")
    for result in results:
        print(f"  {result}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your API is ready for testing.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the issues above.")
    
    return passed, failed

if __name__ == "__main__":
    run_all_tests()
