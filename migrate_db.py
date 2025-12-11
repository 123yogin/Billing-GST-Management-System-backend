#!/usr/bin/env python
"""Database migration script"""
import os
import sys
from flask_migrate import Migrate, init, migrate, upgrade
from app import create_app, db

def run_migrations():
    """Initialize and run database migrations"""
    app = create_app()
    
    with app.app_context():
        # Check if migrations folder exists
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        if not os.path.exists(migrations_dir):
            print("Initializing migrations...")
            try:
                init()
                print("✓ Migrations initialized successfully")
            except Exception as e:
                print(f"✗ Error initializing migrations: {e}")
                print("Migrations folder may already exist or there's a configuration issue")
        
        print("\nSyncing database (Pre-migration)...")
        try:
            upgrade()
            print("✓ Database synced successfully")
        except Exception as e:
            print(f"Warning: Could not sync database: {e}")

        print("\nCreating migration...")
        try:
            migrate(message="Add dealer_id auto-increment column")
            print("✓ Migration created successfully")
        except Exception as e:
            print(f"✗ Error creating migration: {e}")
            return False
        
        print("\nApplying migrations to database...")
        try:
            upgrade()
            print("✓ Database migrated successfully")
            print("\n✅ All migrations completed!")
            return True
        except Exception as e:
            print(f"✗ Error applying migrations: {e}")
            return False

if __name__ == '__main__':
    run_migrations()
