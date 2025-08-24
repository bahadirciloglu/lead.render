-- Supabase Migration SQL
-- Lead Discovery API için veritabanı tabloları

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    company TEXT,
    role TEXT,
    phone TEXT,
    avatar_url TEXT,
    api_calls_count INTEGER DEFAULT 0,
    last_api_call TIMESTAMP WITH TIME ZONE
);

-- Companies table
CREATE TABLE IF NOT EXISTS public.companies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    location TEXT,
    company_size TEXT,
    funding_stage TEXT,
    website TEXT,
    founder TEXT,
    added_manually BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    source TEXT DEFAULT 'manual',
    created_by UUID REFERENCES public.users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pipeline table
CREATE TABLE IF NOT EXISTS public.pipeline (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES public.companies(id) ON DELETE SET NULL,
    company_name TEXT NOT NULL,
    industry TEXT,
    location TEXT,
    company_size TEXT,
    funding_stage TEXT,
    website TEXT,
    founder TEXT,
    deal_value DECIMAL(15,2),
    status TEXT DEFAULT 'Prospecting',
    added_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source TEXT DEFAULT 'Company Collection',
    created_by UUID REFERENCES public.users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat History table
CREATE TABLE IF NOT EXISTS public.chat_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Weeks Data table
CREATE TABLE IF NOT EXISTS public.weeks_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    week_number INTEGER NOT NULL,
    week_name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    data JSONB,  -- JSON formatında haftalık veri
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.users(id),
    UNIQUE(week_number, week_name)
);

-- Archived Weeks table
CREATE TABLE IF NOT EXISTS public.archived_weeks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    week_number INTEGER NOT NULL,
    week_name TEXT NOT NULL,
    archived_data JSONB,  -- JSON formatında arşivlenmiş veri
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archived_by UUID REFERENCES public.users(id)
);

-- LLM Test Results table
CREATE TABLE IF NOT EXISTS public.llm_test_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    test_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    test_data JSONB,  -- JSON formatında test sonuçları
    success BOOLEAN,
    execution_time REAL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.users(id)
);

-- Collected Leads table
CREATE TABLE IF NOT EXISTS public.collected_leads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    industry TEXT,
    company_size TEXT,
    location TEXT,
    funder TEXT,
    notes TEXT,
    source TEXT DEFAULT 'manual',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.users(id),
    updated_by UUID REFERENCES public.users(id)
);

-- Project Management table
CREATE TABLE IF NOT EXISTS public.project_management (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    week_number INTEGER NOT NULL,
    week_name TEXT NOT NULL,
    date_range TEXT,
    current_day INTEGER DEFAULT 1,
    current_day_name TEXT DEFAULT 'Pazartesi',
    executive_summary TEXT,
    issues_plan TEXT,
    upcoming_hackathons TEXT,
    lesson_learned TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.users(id),
    updated_by UUID REFERENCES public.users(id),
    UNIQUE(week_number, week_name)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_companies_name ON public.companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON public.companies(industry);
CREATE INDEX IF NOT EXISTS idx_pipeline_status ON public.pipeline(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_company_name ON public.pipeline(company_name);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON public.chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_weeks_data_week_number ON public.weeks_data(week_number);
CREATE INDEX IF NOT EXISTS idx_project_management_week_number ON public.project_management(week_number);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weeks_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.archived_weeks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.llm_test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.collected_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_management ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all users" ON public.users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND is_admin = true
        )
    );

-- RLS Policies for companies table
CREATE POLICY "Anyone can view companies" ON public.companies
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create companies" ON public.companies
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Users can update own companies" ON public.companies
    FOR UPDATE USING (created_by = auth.uid());

CREATE POLICY "Admins can update all companies" ON public.companies
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND is_admin = true
        )
    );

-- RLS Policies for pipeline table
CREATE POLICY "Anyone can view pipeline" ON public.pipeline
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create pipeline entries" ON public.pipeline
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Users can update own pipeline entries" ON public.pipeline
    FOR UPDATE USING (created_by = auth.uid());

-- RLS Policies for chat_history table
CREATE POLICY "Users can view own chat history" ON public.chat_history
    FOR SELECT USING (user_id = auth.uid() OR user_id IS NULL);

CREATE POLICY "Users can create own chat entries" ON public.chat_history
    FOR INSERT WITH CHECK (user_id = auth.uid() OR user_id IS NULL);

CREATE POLICY "Anonymous users can create chat entries" ON public.chat_history
    FOR INSERT WITH CHECK (user_id IS NULL);

-- RLS Policies for weeks_data table
CREATE POLICY "Anyone can view weeks data" ON public.weeks_data
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create weeks data" ON public.weeks_data
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Users can update own weeks data" ON public.weeks_data
    FOR UPDATE USING (created_by = auth.uid());

-- RLS Policies for project_management table
CREATE POLICY "Anyone can view project management" ON public.project_management
    FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create project entries" ON public.project_management
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Users can update own project entries" ON public.project_management
    FOR UPDATE USING (created_by = auth.uid());

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON public.companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipeline_updated_at BEFORE UPDATE ON public.pipeline
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_weeks_data_updated_at BEFORE UPDATE ON public.weeks_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collected_leads_updated_at BEFORE UPDATE ON public.collected_leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_management_updated_at BEFORE UPDATE ON public.project_management
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (if needed)
-- Note: This should be done after creating the first user through Supabase Auth
-- INSERT INTO public.users (id, email, username, full_name, is_admin, is_verified)
-- VALUES ('default-admin-uuid', 'admin@example.com', 'admin', 'System Administrator', true, true);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- Grant future permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon, authenticated; 