-- Fix RLS Policies for Users and Companies tables
-- Supabase Dashboard'da SQL Editor'da çalıştır

-- 1. Users tablosu için registration policy ekle
CREATE POLICY IF NOT EXISTS "Allow user registration" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 2. Users tablosu için read policy (kendi profilini okuyabilir)
CREATE POLICY IF NOT EXISTS "Users can read own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

-- 3. Companies tablosu için basit policy (test için)
DROP POLICY IF EXISTS "Enable read access for all users" ON public.companies;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON public.companies;
DROP POLICY IF EXISTS "Enable update for users based on created_by" ON public.companies;

-- Basit policy'ler
CREATE POLICY "Allow all operations for now" ON public.companies
    FOR ALL USING (true) WITH CHECK (true);

-- 4. Test için companies tablosunda RLS'yi geçici olarak devre dışı bırak
-- ALTER TABLE public.companies DISABLE ROW LEVEL SECURITY;

-- 5. Policy'lerin durumunu kontrol et
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'companies'); 