-- Add language column to tenders table
ALTER TABLE tenders ADD COLUMN IF NOT EXISTS language VARCHAR(5) DEFAULT 'en';

-- Add comment to the column
COMMENT ON COLUMN tenders.language IS 'Language code for the tender (tr, en, etc.)';

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_tenders_language ON tenders(language);