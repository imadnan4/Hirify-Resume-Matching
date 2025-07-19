"""
Basic test script to verify backend functionality without full dependencies
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if basic imports work"""
    try:
        from app.api.v1.endpoints import resumes, jobs, matching, candidates
        print("✅ All endpoint imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_main_app():
    """Test if main app can be imported"""
    try:
        from main import app
        print("✅ Main app import successful")
        return True
    except ImportError as e:
        print(f"❌ Main app import error: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    required_files = [
        'app/api/v1/endpoints/resumes.py',
        'app/api/v1/endpoints/jobs.py',
        'app/api/v1/endpoints/matching.py',
        'app/api/v1/endpoints/candidates.py',
        'main.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

if __name__ == "__main__":
    print("Starting basic backend tests...")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_main_app,
        test_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print("-" * 30)
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All basic tests passed! Backend structure is good.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
