from supabase_client import get_supabase_client
import asyncio

# Get the Supabase client
supabase = get_supabase_client()

def fetch_data(table_name: str, columns: str = "*"):
    """Fetch data from a table"""
    try:
        response = supabase.table(table_name).select(columns).execute()
        
        if response.data:
            print(f"✅ Data fetched successfully from {table_name}")
            return response.data
        else:
            print(f"❌ No data found in {table_name}")
            return []
            
    except Exception as error:
        print(f"❌ Error fetching data: {error}")
        return None

def insert_data(table_name: str, data: dict):
    """Insert data into a table"""
    try:
        response = supabase.table(table_name).insert(data).execute()
        
        if response.data:
            print(f"✅ Data inserted successfully into {table_name}")
            return response.data
        else:
            print(f"❌ Failed to insert data into {table_name}")
            return None
            
    except Exception as error:
        print(f"❌ Error inserting data: {error}")
        return None

def update_data(table_name: str, data: dict, condition_column: str, condition_value):
    """Update data in a table"""
    try:
        response = (supabase.table(table_name)
                   .update(data)
                   .eq(condition_column, condition_value)
                   .execute())
        
        if response.data:
            print(f"✅ Data updated successfully in {table_name}")
            return response.data
        else:
            print(f"❌ Failed to update data in {table_name}")
            return None
            
    except Exception as error:
        print(f"❌ Error updating data: {error}")
        return None

def delete_data(table_name: str, condition_column: str, condition_value):
    """Delete data from a table"""
    try:
        response = (supabase.table(table_name)
                   .delete()
                   .eq(condition_column, condition_value)
                   .execute())
        
        print(f"✅ Data deleted successfully from {table_name}")
        return response.data
        
    except Exception as error:
        print(f"❌ Error deleting data: {error}")
        return None

def query_with_filters(table_name: str, filters: dict, columns: str = "*"):
    """Query data with multiple filters"""
    try:
        query = supabase.table(table_name).select(columns)
        
        # Apply filters
        for column, value in filters.items():
            query = query.eq(column, value)
        
        response = query.execute()
        
        if response.data:
            print(f"✅ Filtered data fetched successfully from {table_name}")
            return response.data
        else:
            print(f"❌ No data found matching filters in {table_name}")
            return []
            
    except Exception as error:
        print(f"❌ Error querying data: {error}")
        return None


# Add these functions to your existing database_operations.py

def query_with_filters(table_name: str, filters: dict, columns: str = "*"):
    """Query data with multiple filters"""
    try:
        supabase = get_supabase_client()
        query = supabase.table(table_name).select(columns)
        
        # Apply filters
        for column, value in filters.items():
            query = query.eq(column, value)
        
        response = query.execute()
        
        if response.data:
            print(f"✅ Filtered data fetched successfully from {table_name}")
            return response.data
        else:
            print(f"❌ No data found matching filters in {table_name}")
            return []
            
    except Exception as error:
        print(f"❌ Error querying data: {error}")
        return None

def get_table_info(table_name: str):
    """Get basic information about a table"""
    try:
        supabase = get_supabase_client()
        
        # Get row count
        response = supabase.table(table_name).select("*", count="exact").execute()
        row_count = response.count if hasattr(response, 'count') else len(response.data)
        
        print(f"📊 Table '{table_name}' has {row_count} rows")
        
        # Show sample data
        if response.data:
            print(f"📝 Sample columns: {list(response.data[0].keys())}")
        
        return {"row_count": row_count, "sample_data": response.data[:1]}
        
    except Exception as error:
        print(f"❌ Error getting table info: {error}")
        return None
