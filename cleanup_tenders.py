#!/usr/bin/env python3
"""
Cleanup duplicate tender records in Supabase database.
Keeps only the newest record for each deal_id.
"""

from supabase_database import SupabaseDatabaseManager
from collections import defaultdict

def cleanup_duplicate_tenders():
    """Remove duplicate tender records, keeping only the newest for each deal_id"""
    
    # Initialize database manager
    db = SupabaseDatabaseManager()
    
    try:
        # Get all tender records
        print("🔍 Fetching all tender records...")
        tenders = db.get_tenders(limit=1000)
        print(f"📊 Found {len(tenders)} total tender records")
        
        if not tenders:
            print("ℹ️ No tender records found")
            return
            
        # Group tenders by deal_id
        tenders_by_deal = defaultdict(list)
        for tender in tenders:
            deal_id = tender.get('deal_id')
            if deal_id:
                tenders_by_deal[deal_id].append(tender)
            else:
                print(f"⚠️ Found tender without deal_id: {tender.get('id')}")
        
        print(f"📊 Found {len(tenders_by_deal)} unique deal_ids")
        
        # Find duplicates and identify records to delete
        records_to_delete = []
        
        for deal_id, deal_tenders in tenders_by_deal.items():
            if len(deal_tenders) > 1:
                print(f"🔍 Deal {deal_id} has {len(deal_tenders)} tender records")
                
                # Sort by created_at (newest first)
                sorted_tenders = sorted(deal_tenders, 
                                      key=lambda x: x.get('created_at', ''), 
                                      reverse=True)
                
                # Keep the newest, mark others for deletion
                newest_tender = sorted_tenders[0]
                duplicates = sorted_tenders[1:]
                
                print(f"  ✅ Keeping newest: {newest_tender.get('id')} (created: {newest_tender.get('created_at')})")
                
                for duplicate in duplicates:
                    print(f"  ❌ Marking for deletion: {duplicate.get('id')} (created: {duplicate.get('created_at')})")
                    records_to_delete.append(duplicate.get('id'))
        
        if not records_to_delete:
            print("✅ No duplicate records found!")
            return
            
        print(f"\n🗑️ Total records to delete: {len(records_to_delete)}")
        
        # Delete duplicate records
        deleted_count = 0
        for tender_id in records_to_delete:
            try:
                success = db.delete_tender(tender_id)
                if success:
                    deleted_count += 1
                    print(f"✅ Deleted tender: {tender_id}")
                else:
                    print(f"❌ Failed to delete tender: {tender_id}")
            except Exception as e:
                print(f"❌ Error deleting tender {tender_id}: {e}")
        
        print(f"\n📊 Cleanup Summary:")
        print(f"  • Total records before: {len(tenders)}")
        print(f"  • Records deleted: {deleted_count}")
        print(f"  • Records remaining: {len(tenders) - deleted_count}")
        print(f"  • Unique deals: {len(tenders_by_deal)}")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_duplicate_tenders()
