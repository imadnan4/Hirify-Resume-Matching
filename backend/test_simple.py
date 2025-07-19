"""
Simple test to check core imports
"""
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test basic imports without services"""
    try:
        # Test schema imports
        from app.schemas.resume import Resume, ResumeCreate
        print("✅ Resume schemas imported successfully")
        
        from app.schemas.job_description import JobDescription, JobDescriptionCreate
        print("✅ Job schemas imported successfully")
        
        from app.schemas.candidate import Candidate, CandidateCreate
        print("✅ Candidate schemas imported successfully")
        
        from app.schemas.match import Match, MatchCreate
        print("✅ Match schemas imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Schema import failed: {e}")
        return False

def test_main_app():
    """Test main app import"""
    try:
        from main import app
        print("✅ Main app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting simple import tests...")
    print("=" * 50)
    
    if test_basic_imports():
        print("\n✅ All schema imports successful!")
        
        if test_main_app():
            print("✅ Main app import successful!")
            print("\n🎉 All basic imports working!")
        else:
            print("❌ Main app import failed")
    else:
        print("❌ Schema imports failed")
