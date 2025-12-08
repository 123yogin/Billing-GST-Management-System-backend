"""
Database migration to add khata_no column to dealers table
"""
import sqlite3
import os

# Get the database path
db_path = os.path.join('instance', 'billing_db.sqlite')

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if khata_no column exists
    cursor.execute("PRAGMA table_info(dealers)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'khata_no' not in columns:
        print("Adding khata_no column to dealers table...")
        cursor.execute("ALTER TABLE dealers ADD COLUMN khata_no TEXT")
        conn.commit()
        print("✓ Column added successfully!")
    else:
        print("✓ khata_no column already exists!")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(dealers)")
    columns = cursor.fetchall()
    print("\nCurrent dealers table schema:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✓ Migration completed successfully!")

except Exception as e:
    print(f"✗ Error: {e}")
    if conn:
        conn.rollback()
        conn.close()
