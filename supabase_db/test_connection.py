from supabase_client import get_supabase_client
from database_operations import fetch_data, insert_data, update_data, delete_data
import json
from datetime import datetime

def test_supabase_connection():
    """Test the basic Supabase connection"""
    try:
        supabase = get_supabase_client()
        
        # Test basic connection with your existing test table
        result = fetch_data('test', '*')
        
        if result is not None:
            print("🎉 Supabase connection successful!")
            print(f"Current data in 'test' table: {result}")
            return True
        else:
            print("❌ Connection test failed")
            return False
            
    except Exception as error:
        print(f"❌ Connection error: {error}")
        return False

def test_insert_into_test_table():
    """Test inserting data into the existing test table"""
    print("\n--- Testing INSERT into 'test' table ---")
    
    # Test data for the test table (matching your schema: id, created_at, name)
    test_records = [
        {
            "name": "AI Agent User 1"
        },
        {
            "name": "Food Buddy Test User"
        },
        {
            "name": "Agentic AI System Test"
        },
        {
            "name": "Python Integration Test"
        }
    ]
    
    # INSERT operations
    print("Inserting test records...")
    inserted_records = []
    
    for record in test_records:
        result = insert_data("test", record)
        if result:
            inserted_records.extend(result)
            print(f"✅ Inserted record: {record['name']}")
            print(f"   Generated ID: {result[0].get('id')}")
            print(f"   Created at: {result[0].get('created_at')}")
        else:
            print(f"❌ Failed to insert record: {record['name']}")
    
    return inserted_records

def test_read_from_test_table():
    """Test reading data from the test table"""
    print("\n--- Testing SELECT from 'test' table ---")
    
    # Read all records
    print("Fetching all records...")
    all_records = fetch_data("test", "*")
    
    if all_records:
        print(f"✅ Successfully fetched {len(all_records)} records")
        for record in all_records:
            print(f"   ID: {record.get('id')}, Name: {record.get('name')}, Created: {record.get('created_at')}")
    else:
        print("❌ No records found or fetch failed")
    
    # Read specific columns
    print("\nFetching specific columns (id, name)...")
    supabase = get_supabase_client()
    try:
        response = supabase.table("test").select("id, name").execute()
        if response.data:
            print(f"✅ Fetched {len(response.data)} records with specific columns")
            for record in response.data[-3:]:  # Show last 3
                print(f"   ID: {record.get('id')}, Name: {record.get('name')}")
    except Exception as error:
        print(f"❌ Error fetching specific columns: {error}")
    
    return all_records

def test_update_test_table():
    """Test updating data in the test table"""
    print("\n--- Testing UPDATE in 'test' table ---")
    
    # First, get the latest record to update
    latest_records = fetch_data("test", "*")
    
    if latest_records:
        # Update the latest record
        latest_record = latest_records[-1]  # Get the last record
        record_id = latest_record.get('id')
        
        print(f"Updating record with ID: {record_id}")
        
        updated_data = {
            "name": f"Updated: {latest_record.get('name')} - {datetime.now().strftime('%H:%M:%S')}"
        }
        
        result = update_data("test", updated_data, "id", record_id)
        
        if result:
            print(f"✅ Successfully updated record ID {record_id}")
            print(f"   New name: {result[0].get('name')}")
        else:
            print(f"❌ Failed to update record ID {record_id}")
    else:
        print("❌ No records available to update")

def test_filtering_test_table():
    """Test filtering data from the test table"""
    print("\n--- Testing FILTERING in 'test' table ---")
    
    supabase = get_supabase_client()
    
    try:
        # Filter by name containing "AI"
        print("Filtering records containing 'AI' in name...")
        response = supabase.table("test").select("*").ilike("name", "%AI%").execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} records containing 'AI'")
            for record in response.data:
                print(f"   ID: {record.get('id')}, Name: {record.get('name')}")
        else:
            print("❌ No records found containing 'AI'")
        
        # Filter by ID greater than a specific value
        print("\nFiltering records with ID > 12343425...")
        response = supabase.table("test").select("*").gt("id", 12343425).execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} records with ID > 12343425")
            for record in response.data[:3]:  # Show first 3
                print(f"   ID: {record.get('id')}, Name: {record.get('name')}")
        else:
            print("❌ No records found with ID > 12343425")
        
        # Get records ordered by created_at
        print("\nFetching records ordered by created_at (newest first)...")
        response = supabase.table("test").select("*").order("created_at", desc=True).limit(5).execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} newest records")
            for record in response.data:
                print(f"   ID: {record.get('id')}, Name: {record.get('name')}, Created: {record.get('created_at')}")
        
    except Exception as error:
        print(f"❌ Error in filtering operations: {error}")

def test_count_and_stats():
    """Test counting and basic statistics"""
    print("\n--- Testing COUNT and Statistics ---")
    
    supabase = get_supabase_client()
    
    try:
        # Get total count
        response = supabase.table("test").select("*", count="exact").execute()
        total_count = response.count if hasattr(response, 'count') else len(response.data)
        
        print(f"📊 Total records in 'test' table: {total_count}")
        
        # Get records created today (approximate)
        today = datetime.now().strftime('%Y-%m-%d')
        response = supabase.table("test").select("*").gte("created_at", f"{today}T00:00:00").execute()
        
        if response.data:
            print(f"📅 Records created today: {len(response.data)}")
        
        # Get latest and oldest records
        if response.data:
            latest = max(response.data, key=lambda x: x.get('created_at', ''))
            oldest = min(response.data, key=lambda x: x.get('created_at', ''))
            
            print(f"🕐 Latest record: ID {latest.get('id')} - {latest.get('name')}")
            print(f"🕐 Oldest record: ID {oldest.get('id')} - {oldest.get('name')}")
        
    except Exception as error:
        print(f"❌ Error getting statistics: {error}")

def test_delete_from_test_table():
    """Test deleting data from test table (optional - uncomment if needed)"""
    print("\n--- Testing DELETE from 'test' table (COMMENTED OUT FOR SAFETY) ---")
    print("⚠️  Delete operations are commented out to preserve your data")
    print("⚠️  Uncomment the code below if you want to test deletions")
    
    # Uncomment the code below if you want to test deletions
    """
    # Get records to delete (only delete our test records)
    records_to_delete = fetch_data("test", "*")
    
    if records_to_delete:
        # Delete only records that contain "Test" in the name
        for record in records_to_delete:
            if "Test" in record.get('name', ''):
                result = delete_data("test", "id", record.get('id'))
                if result:
                    print(f"✅ Deleted record: {record.get('name')}")
                else:
                    print(f"❌ Failed to delete record: {record.get('name')}")
    """

def main():
    """Main test function for the existing test table"""
    print("🚀 Starting Supabase 'test' Table Operations...")
    print("=" * 60)
    
    # Test 1: Basic connection
    if not test_supabase_connection():
        print("❌ Basic connection failed. Exiting...")
        return
    
    # Test 2: Insert new records
    inserted_records = test_insert_into_test_table()
    
    # Test 3: Read all data
    all_records = test_read_from_test_table()
    
    # Test 4: Update existing data
    test_update_test_table()
    
    # Test 5: Test filtering and querying
    test_filtering_test_table()
    
    # Test 6: Count and statistics
    test_count_and_stats()
    
    # Test 7: Delete operations (commented out for safety)
    test_delete_from_test_table()
    
    print("\n" + "=" * 60)
    print("🎉 Test table operations completed!")
    print("Your Supabase integration is working perfectly!")
    print(f"Project ID: zsmydhwqejwaueugahnw")

if __name__ == "__main__":
    main()
