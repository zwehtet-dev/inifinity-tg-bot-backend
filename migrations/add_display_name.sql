-- Add display_name column to thai_bank_accounts
ALTER TABLE thai_bank_accounts ADD COLUMN display_name VARCHAR(50);

-- Add display_name column to myanmar_bank_accounts
ALTER TABLE myanmar_bank_accounts ADD COLUMN display_name VARCHAR(50);
