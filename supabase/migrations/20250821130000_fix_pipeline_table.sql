-- Fix pipeline table structure and RLS
-- Drop and recreate pipeline table to ensure correct structure

-- Drop existing table if exists
DROP TABLE IF EXISTS pipeline CASCADE;

-- Create pipeline table with all necessary columns
CREATE TABLE pipeline (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    location VARCHAR(255),
    company_size VARCHAR(100),
    funding_stage VARCHAR(100),
    website VARCHAR(255),
    founder VARCHAR(255),
    deal_value DECIMAL(15,2),
    status VARCHAR(100) DEFAULT 'prospecting',
    source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Enable Row Level Security
ALTER TABLE pipeline ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Allow all operations on pipeline" ON pipeline;

-- Create policy to allow all operations (for now)
CREATE POLICY "Allow all operations on pipeline" ON pipeline
    FOR ALL USING (true)
    WITH CHECK (true);

-- Insert test record
INSERT INTO pipeline (company_name, industry, location, company_size, funding_stage, website, founder, deal_value, status, source)
VALUES ('Test Pipeline Company', 'Technology', 'Istanbul', '10-50', 'Seed', 'test.com', 'Test Founder', 25000, 'prospecting', 'test');

-- Verify table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'pipeline' 
ORDER BY ordinal_position; 