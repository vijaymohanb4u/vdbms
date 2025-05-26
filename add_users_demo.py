#!/usr/bin/env python3
"""Demo script showing how to add users to the users table."""

from sql_json_engine import SQLToJSONEngine

def main():
    engine = SQLToJSONEngine()
    
    print("=== Adding Users to Users Table ===\n")
    
    # Show current users
    result = engine.execute_sql("SELECT * FROM users")
    print(f"Current users in table: {result.get('count', 0)}")
    
    # 1. Add single user with specific ID
    print("\n1. Adding user with specific ID:")
    sql = "INSERT INTO users VALUES (10, 'Alice Johnson', 28)"
    print(f"SQL: {sql}")
    result = engine.execute_sql(sql)
    print(f"Result: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # 2. Add user without ID (auto-generated)
    print("\n2. Adding user with auto-generated ID:")
    sql = "INSERT INTO users (name, age) VALUES ('Mike Davis', 42)"
    print(f"SQL: {sql}")
    result = engine.execute_sql(sql)
    print(f"Result: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # 3. Add multiple users at once
    print("\n3. Adding multiple users at once:")
    sql = "INSERT INTO users (name, age) VALUES ('Sarah Wilson', 29), ('Emma Brown', 26)"
    print(f"SQL: {sql}")
    result = engine.execute_sql(sql)
    print(f"Result: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # 4. Add user with only name (age optional)
    print("\n4. Adding user with only name:")
    sql = "INSERT INTO users (name) VALUES ('Tom Anderson')"
    print(f"SQL: {sql}")
    result = engine.execute_sql(sql)
    print(f"Result: {'✓' if result['success'] else '✗'} {result.get('message', result.get('error', ''))}")
    
    # Show final results
    print("\n=== Final User List ===")
    result = engine.execute_sql("SELECT id, name, age FROM users")
    if result['success']:
        print(f"Total users: {result['count']}")
        for i, user in enumerate(result['records'], 1):
            age_str = f"age {user['age']}" if user.get('age') else "age unknown"
            print(f"  {i}. {user['name']} ({age_str}) [ID: {user.get('id', 'auto')}]")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main() 