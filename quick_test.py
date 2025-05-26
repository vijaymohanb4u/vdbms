#!/usr/bin/env python3
"""Quick test of SQL-JSON integration."""

from sql_json_engine import SQLToJSONEngine

def main():
    engine = SQLToJSONEngine()
    
    # Clean up
    for table in engine.list_tables():
        engine.drop_table(table)
    
    print("=== SQL-JSON Integration Test ===")
    
    # Create table
    result = engine.execute_sql("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), age INT)")
    print(f"1. Create table: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # Insert data
    result = engine.execute_sql("INSERT INTO users VALUES (1, 'John Doe', 30)")
    print(f"2. Insert data: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # Insert more data
    result = engine.execute_sql("INSERT INTO users VALUES (2, 'Jane Smith', 25), (3, 'Bob Wilson', 35)")
    print(f"3. Insert multiple: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # Query all
    result = engine.execute_sql("SELECT * FROM users")
    print(f"4. Select all: {'✓' if result['success'] else '✗'} Found {result.get('count', 0)} records")
    
    # Query with WHERE
    result = engine.execute_sql("SELECT name FROM users WHERE age > 28")
    print(f"5. Select filtered: {'✓' if result['success'] else '✗'} Found {result.get('count', 0)} records")
    if result['success'] and result['records']:
        names = [r['name'] for r in result['records']]
        print(f"   Names: {names}")
    
    # Update data
    result = engine.execute_sql("UPDATE users SET age = 31 WHERE name = 'John Doe'")
    print(f"6. Update data: {'✓' if result['success'] else '✗'} Updated {result.get('updated_count', 0)} records")
    
    # Delete data
    result = engine.execute_sql("DELETE FROM users WHERE age < 30")
    print(f"7. Delete data: {'✓' if result['success'] else '✗'} Deleted {result.get('deleted_count', 0)} records")
    
    # Final count
    result = engine.execute_sql("SELECT * FROM users")
    print(f"8. Final count: {'✓' if result['success'] else '✗'} {result.get('count', 0)} records remaining")
    
    # Show tables
    tables = engine.list_tables()
    print(f"9. Tables: {tables}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 