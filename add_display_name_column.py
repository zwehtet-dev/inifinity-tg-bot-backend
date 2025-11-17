"""
Quick script to add display_name column to bank tables.
Run this from the backend directory: python add_display_name_column.py
"""
import sqlite3
import os

# Get database path - try multiple locations
possible_paths = [
    os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
    os.path.join(os.path.dirname(__file__), 'instance', 'database.db'),
    os.path.join(os.path.dirname(__file__), 'database.db'),
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print(f"❌ Database not found. Tried:")
    for path in possible_paths:
        print(f"  - {path}")
    print("\nPlease check your database location.")
    exit(1)

print(f"📁 Database: {db_path}")
print("=" * 60)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check and add display_name to thai_bank_accounts
    print("Checking thai_bank_accounts...")
    cursor.execute("PRAGMA table_info(thai_bank_accounts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'display_name' not in columns:
        print("  Adding display_name column...")
        cursor.execute("ALTER TABLE thai_bank_accounts ADD COLUMN display_name VARCHAR(50)")
        conn.commit()
        print("  ✅ Added display_name to thai_bank_accounts")
    else:
        print("  ✅ display_name already exists in thai_bank_accounts")
    
    # Check and add display_name to myanmar_bank_accounts
    print("\nChecking myanmar_bank_accounts...")
    cursor.execute("PRAGMA table_info(myanmar_bank_accounts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'display_name' not in columns:
        print("  Adding display_name column...")
        cursor.execute("ALTER TABLE myanmar_bank_accounts ADD COLUMN display_name VARCHAR(50)")
        conn.commit()
        print("  ✅ Added display_name to myanmar_bank_accounts")
    else:
        print("  ✅ display_name already exists in myanmar_bank_accounts")
    
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print("\nYou can now restart your backend server.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
    exit(1)
finally:
    conn.close()
