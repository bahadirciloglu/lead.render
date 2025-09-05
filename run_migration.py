#!/usr/bin/env python3
"""
Run database migration to add language column
"""

from supabase_config import supabase_config
import sys

def run_migration():
    """Run the language column migration"""
    try:
        print("🔄 Running database migration...")
        
        # Get admin client for DDL operations
        client = supabase_config.get_admin_client()
        
        # Read migration SQL
        with open('add_language_column.sql', 'r') as f:
            migration_sql = f.read()
        
        print("📝 Executing migration SQL...")
        print(f"SQL: {migration_sql}")
        
        # Execute migration using RPC call
        result = client.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        print("✅ Migration completed successfully!")
        print(f"Result: {result}")
        
        # Test the new column
        print("🧪 Testing new column...")
        test_result = client.table('tenders').select('*').limit(1).execute()
        print(f"✅ Test query successful: {len(test_result.data)} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)