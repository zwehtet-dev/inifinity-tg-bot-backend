"""
Migration script to add amount field to bank accounts tables.
Run this script to update existing database schema.
"""
import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if amount column exists in thai_bank_accounts
        cursor.execute("PRAGMA table_info(thai_bank_accounts)")
        thai_columns = [column[1] for column in cursor.fetchall()]
        
        if 'amount' not in thai_columns:
            print("Adding amount column to thai_bank_accounts...")
            cursor.execute("ALTER TABLE thai_bank_accounts ADD COLUMN amount REAL")
            print("✓ Added amount column to thai_bank_accounts")
        else:
            print("✓ Amount column already exists in thai_bank_accounts")
        
        # Check if amount column exists in myanmar_bank_accounts
        cursor.execute("PRAGMA table_info(myanmar_bank_accounts)")
        myanmar_columns = [column[1] for column in cursor.fetchall()]
        
        if 'amount' not in myanmar_columns:
            print("Adding amount column to myanmar_bank_accounts...")
            cursor.execute("ALTER TABLE myanmar_bank_accounts ADD COLUMN amount REAL")
            print("✓ Added amount column to myanmar_bank_accounts")
        else:
            print("✓ Amount column already exists in myanmar_bank_accounts")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
