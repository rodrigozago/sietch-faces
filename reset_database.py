#!/usr/bin/env python3
"""
Reset database - Remove and recreate database
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, engine, Base

def reset_database():
    """Drop all tables and recreate them"""
    db_file = "sietch_faces.db"
    
    print("🗑️  Resetting database...")
    
    # Backup old database if it exists
    if os.path.exists(db_file):
        backup_file = f"{db_file}.backup"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        os.rename(db_file, backup_file)
        print(f"📦 Old database backed up to: {backup_file}")
    
    # Drop all tables
    print("🔨 Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    print("🏗️  Creating tables...")
    init_db()
    
    print("✅ Database reset complete!")
    print("\nYou can now:")
    print("  1. Start the API: uvicorn app.main:app --reload")
    print("  2. Upload new images")

if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
