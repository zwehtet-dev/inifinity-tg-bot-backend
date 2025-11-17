"""
Migration: Add display_name column to bank tables

This adds a display_name field to both ThaiBankAccount and MyanmarBankAccount tables
for use in balance notifications.
"""
from models import db, ThaiBankAccount, MyanmarBankAccount


def upgrade():
    """Add display_name column to bank tables."""
    print("Adding display_name column to bank tables...")
    
    # Add display_name to ThaiBankAccount
    with db.engine.connect() as conn:
        # Check if column exists
        result = conn.execute(db.text(
            "SELECT COUNT(*) FROM pragma_table_info('thai_bank_accounts') "
            "WHERE name='display_name'"
        ))
        if result.scalar() == 0:
            conn.execute(db.text(
                "ALTER TABLE thai_bank_accounts ADD COLUMN display_name VARCHAR(50)"
            ))
            conn.commit()
            print("✓ Added display_name to thai_bank_accounts")
        else:
            print("✓ display_name already exists in thai_bank_accounts")
    
    # Add display_name to MyanmarBankAccount
    with db.engine.connect() as conn:
        result = conn.execute(db.text(
            "SELECT COUNT(*) FROM pragma_table_info('myanmar_bank_accounts') "
            "WHERE name='display_name'"
        ))
        if result.scalar() == 0:
            conn.execute(db.text(
                "ALTER TABLE myanmar_bank_accounts ADD COLUMN display_name VARCHAR(50)"
            ))
            conn.commit()
            print("✓ Added display_name to myanmar_bank_accounts")
        else:
            print("✓ display_name already exists in myanmar_bank_accounts")
    
    print("Migration completed successfully!")


def downgrade():
    """Remove display_name column from bank tables."""
    print("Removing display_name column from bank tables...")
    
    # SQLite doesn't support DROP COLUMN directly, so we'd need to recreate tables
    # For now, just log that downgrade is not supported
    print("⚠️  Downgrade not supported for SQLite. Column will remain but can be ignored.")


if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        upgrade()
