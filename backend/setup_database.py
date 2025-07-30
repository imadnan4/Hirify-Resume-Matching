#!/usr/bin/env python3
"""
Database setup script for Hirify backend.
This script creates all the database tables defined in the models.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models.user import User, UserSession, PasswordResetToken, AuditLog
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match import Match
from app.models.candidate import Candidate

def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        
        # List the tables that were created
        print("\nTables created:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n🎉 Database setup completed successfully!")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
