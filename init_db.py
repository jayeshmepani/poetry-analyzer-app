#!/usr/bin/env python3
"""
Database Initialization Script
Poetry Analyzer App

This script initializes the database with all required tables.
Supports SQLite, MySQL, and PostgreSQL.

Usage:
    python init_db.py
    
For MySQL/PostgreSQL, first update your .env file with the correct DATABASE_URL
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import (
    engine, 
    Base, 
    SessionLocal, 
    test_connection, 
    init_db,
    get_database_info,
    DB_TYPE,
    DATABASE_URL
)
from app.models import db_models
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print initialization banner"""
    print("\n" + "=" * 70)
    print("  Poetry Analyzer App - Database Initialization")
    print("=" * 70 + "\n")


def print_database_info():
    """Print current database configuration"""
    print("📊 Database Configuration:")
    print(f"   Type: {DB_TYPE}")
    print(f"   URL: {'***' if 'password' in DATABASE_URL else DATABASE_URL}")
    print()


def check_database_connection():
    """Check if database connection is working"""
    print("🔍 Testing database connection...")
    if test_connection():
        print("✅ Database connection successful\n")
        return True
    else:
        print("❌ Database connection failed\n")
        return False


def create_tables():
    """Create all database tables"""
    print("📋 Creating database tables...")
    try:
        init_db()
        print("✅ Tables created successfully\n")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}\n")
        return False


def verify_tables():
    """Verify that all required tables exist"""
    print("🔍 Verifying tables...")
    try:
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'analysis_results',
            'database_stats',
            'user_settings'
        ]
        
        print(f"   Found tables: {tables}")
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"⚠️  Missing tables: {missing}")
            return False
        else:
            print("✅ All required tables present\n")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {e}\n")
        return False


def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data (optional)...")
    try:
        from datetime import datetime
        from app.models.db_models import AnalysisResult
        
        db = SessionLocal()
        try:
            # Check if data already exists
            count = db.query(AnalysisResult).count()
            if count > 0:
                print(f"   ⏭️  Skipping: {count} analyses already exist")
                return
            
            # Create sample analysis
            sample = AnalysisResult(
                title="Sample Poetry Analysis",
                text="Roses are red,\nViolets are blue,\nSugar is sweet,\nAnd so are you.",
                language="en",
                poetic_form="quatrain",
                overall_score=7.5,
                technical_craft_score=7.0,
                language_diction_score=8.0,
                imagery_voice_score=7.5,
                emotional_impact_score=8.0,
                cultural_fidelity_score=7.0,
                originality_score=6.5,
                word_count=17,
                line_count=4,
                strictness_level=7,
                executive_summary="A classic quatrain with simple yet effective imagery.",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(sample)
            db.commit()
            
            print("   ✅ Sample data created\n")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"   ⚠️  Could not create sample data: {e}\n")


def show_database_stats():
    """Show database statistics"""
    print("📊 Database Statistics:")
    try:
        from app.models.db_models import AnalysisResult
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            # Total analyses
            total = db.query(AnalysisResult).count()
            print(f"   Total analyses: {total}")
            
            # By language
            by_language = db.query(
                AnalysisResult.language, 
                func.count(AnalysisResult.id)
            ).group_by(AnalysisResult.language).all()
            
            if by_language:
                print("   By language:")
                for lang, count in by_language:
                    print(f"      {lang}: {count}")
            
            # Database size
            db_info = get_database_info()
            if db_info.get('status') == 'connected':
                print(f"   Database size: {db_info.get('size_mb', 0)} MB")
            
            print()
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"   ⚠️  Could not get stats: {e}\n")


def main():
    """Main initialization function"""
    print_banner()
    print_database_info()
    
    # Step 1: Check connection
    if not check_database_connection():
        print("\n❌ Database initialization failed!")
        print("\nTroubleshooting:")
        if DB_TYPE == "mysql":
            print("   1. Make sure MySQL is running: sudo systemctl status mysql")
            print("   2. Check credentials in .env file")
            print("   3. Verify database exists: mysql -u poetry_user -p -e 'SHOW DATABASES;'")
        elif DB_TYPE == "postgresql":
            print("   1. Make sure PostgreSQL is running: sudo systemctl status postgresql")
            print("   2. Check credentials in .env file")
            print("   3. Verify database exists: sudo -u postgres psql -l")
        elif DB_TYPE == "sqlite":
            print("   1. Check file permissions")
            print("   2. Ensure directory is writable")
        return 1
    
    # Step 2: Create tables
    if not create_tables():
        print("\n❌ Table creation failed!")
        return 1
    
    # Step 3: Verify tables
    if not verify_tables():
        print("\n⚠️  Table verification failed, but continuing...")
    
    # Step 4: Create sample data
    create_sample_data()
    
    # Step 5: Show statistics
    show_database_stats()
    
    print("=" * 70)
    print("  ✅ Database initialization completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("   1. Start the application: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 9000")
    print("   2. Open browser: http://localhost:9000/admin")
    print("   3. Try analyzing some poetry!")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
