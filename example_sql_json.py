#!/usr/bin/env python3
"""
SQL-JSON Database Engine Example

This script demonstrates the complete functionality of the integrated
SQL parser and JSON CRUD system.
"""

from sql_json_engine import SQLToJSONEngine
from config import config
import json


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title.upper()}")
    print(f"{'='*60}")


def print_result(sql, result):
    """Print SQL execution result in a formatted way."""
    print(f"\nSQL: {sql}")
    if result["success"]:
        print("✓ SUCCESS")
        if "records" in result and result["records"]:
            print(f"Records found: {result['count']}")
            for i, record in enumerate(result["records"][:3], 1):
                print(f"  {i}. {record}")
            if result["count"] > 3:
                print(f"  ... and {result['count'] - 3} more records")
        elif "inserted_count" in result:
            print(f"Inserted: {result['inserted_count']} records")
        elif "updated_count" in result:
            print(f"Updated: {result['updated_count']} records")
        elif "deleted_count" in result:
            print(f"Deleted: {result['deleted_count']} records")
        elif "message" in result:
            print(f"Message: {result['message']}")
    else:
        print(f"✗ ERROR: {result['error']}")


def demonstrate_sql_json_engine():
    """Comprehensive demonstration of SQL-JSON engine features."""
    print("SQL-to-JSON Database Engine Demonstration")
    print("This example shows all major features of the integrated system.")
    
    # Initialize engine
    engine = SQLToJSONEngine()
    
    # Clean up any existing tables for fresh demo
    for table in engine.list_tables():
        engine.drop_table(table)
    
    print_section("1. Schema Definition")
    
    # Create tables with various constraints
    schemas = [
        """CREATE TABLE users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE,
            age INT,
            status VARCHAR(20)
        )""",
        
        """CREATE TABLE products (
            product_id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price FLOAT,
            category VARCHAR(50),
            in_stock INT
        )""",
        
        """CREATE TABLE orders (
            order_id INT PRIMARY KEY,
            user_id INT,
            product_id INT,
            quantity INT,
            order_date VARCHAR(20),
            total_amount FLOAT
        )"""
    ]
    
    for sql in schemas:
        result = engine.execute_sql(sql)
        print_result(sql.replace('\n', ' ').replace('  ', ' '), result)
    
    print_section("2. Data Insertion")
    
    # Insert sample data
    inserts = [
        # Users
        "INSERT INTO users (name, email, age, status) VALUES ('John Doe', 'john@example.com', 30, 'active')",
        "INSERT INTO users (name, email, age, status) VALUES ('Jane Smith', 'jane@example.com', 25, 'active'), ('Bob Wilson', 'bob@example.com', 35, 'inactive')",
        
        # Products
        "INSERT INTO products VALUES (1, 'Laptop Pro', 1299.99, 'Electronics', 15)",
        "INSERT INTO products VALUES (2, 'Wireless Mouse', 29.99, 'Electronics', 50), (3, 'Office Chair', 199.99, 'Furniture', 8)",
        
        # Orders
        "INSERT INTO orders VALUES (1001, 1, 1, 1, '2023-12-01', 1299.99)",
        "INSERT INTO orders VALUES (1002, 2, 2, 2, '2023-12-02', 59.98), (1003, 3, 3, 1, '2023-12-03', 199.99)"
    ]
    
    for sql in inserts:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("3. Basic Queries")
    
    # Simple SELECT queries
    queries = [
        "SELECT * FROM users",
        "SELECT name, email FROM users",
        "SELECT product_id, name, price FROM products",
        "SELECT COUNT(*) as total_orders FROM orders"  # Note: COUNT not implemented yet
    ]
    
    for sql in queries[:-1]:  # Skip COUNT for now
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("4. Filtered Queries")
    
    # WHERE clause queries
    filtered_queries = [
        "SELECT * FROM users WHERE age > 28",
        "SELECT * FROM products WHERE price < 100",
        "SELECT * FROM orders WHERE quantity > 1",
        "SELECT name, email FROM users WHERE status = 'active'"
    ]
    
    for sql in filtered_queries:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("5. Pattern Matching")
    
    # LIKE operator queries
    pattern_queries = [
        "SELECT * FROM users WHERE name LIKE 'J%'",
        "SELECT * FROM products WHERE name LIKE '%Pro%'",
        "SELECT * FROM users WHERE email LIKE '%@example.com'"
    ]
    
    for sql in pattern_queries:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("6. Complex Conditions")
    
    # Complex WHERE clauses
    complex_queries = [
        "SELECT * FROM users WHERE age > 25 AND status = 'active'",
        "SELECT * FROM products WHERE (price > 100 AND category = 'Electronics') OR category = 'Furniture'",
        "SELECT * FROM orders WHERE quantity > 1 OR total_amount > 1000"
    ]
    
    for sql in complex_queries:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("7. Data Updates")
    
    # UPDATE operations
    updates = [
        "UPDATE users SET age = 31 WHERE name = 'John Doe'",
        "UPDATE products SET price = 1199.99 WHERE product_id = 1",
        "UPDATE users SET status = 'premium' WHERE age > 30"
    ]
    
    for sql in updates:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    # Show updated data
    result = engine.execute_sql("SELECT * FROM users")
    print_result("SELECT * FROM users (after updates)", result)
    
    print_section("8. Data Deletion")
    
    # DELETE operations
    deletes = [
        "DELETE FROM orders WHERE quantity = 1",
        "DELETE FROM products WHERE in_stock < 10"
    ]
    
    for sql in deletes:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("9. Constraint Validation")
    
    # Demonstrate constraint violations
    constraint_tests = [
        # Duplicate primary key
        "INSERT INTO users (id, name, email) VALUES (1, 'Test User', 'test@example.com')",
        
        # Duplicate unique email
        "INSERT INTO users (name, email, age) VALUES ('Another User', 'john@example.com', 25)",
        
        # NOT NULL violation
        "INSERT INTO users (email, age) VALUES ('noname@example.com', 25)"
    ]
    
    for sql in constraint_tests:
        result = engine.execute_sql(sql)
        print_result(sql, result)
    
    print_section("10. Schema Management")
    
    # Show table information
    print("\nAvailable Tables:")
    tables = engine.list_tables()
    for table in tables:
        print(f"  - {table}")
    
    print("\nTable Schemas:")
    for table in tables:
        schema = engine.describe_table(table)
        print(f"\n{table.upper()}:")
        for col_name, col_info in schema["columns"].items():
            constraints = ", ".join(col_info.get("constraints", []))
            size_info = f"({col_info['size']})" if col_info.get('size') else ""
            constraint_info = f" [{constraints}]" if constraints else ""
            print(f"  - {col_name}: {col_info['type']}{size_info}{constraint_info}")
    
    print_section("11. Final Data State")
    
    # Show final state of all tables
    for table in engine.list_tables():
        result = engine.execute_sql(f"SELECT * FROM {table}")
        print(f"\n{table.upper()} ({result['count']} records):")
        if result["records"]:
            for i, record in enumerate(result["records"], 1):
                # Show only key fields for readability
                key_fields = {}
                for key in ['id', 'name', 'email', 'product_id', 'order_id', 'price', 'quantity']:
                    if key in record:
                        key_fields[key] = record[key]
                print(f"  {i}. {key_fields}")
        else:
            print("  (no records)")
    
    print_section("12. Configuration and File Storage")
    
    # Show configuration
    print(f"\nDatabase Directory: {config.db_directory}")
    print(f"Pretty Print: {config.pretty_print}")
    print(f"Auto Create Directory: {config.auto_create_directory}")
    
    # Show generated files
    import os
    if os.path.exists(config.db_directory):
        print(f"\nGenerated Files in {config.db_directory}:")
        for file in os.listdir(config.db_directory):
            file_path = os.path.join(config.db_directory, file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size} bytes)")
    
    print_section("Summary")
    
    print("""
This demonstration showed:

✓ Schema Definition - CREATE TABLE with constraints
✓ Data Insertion - INSERT with single and multiple rows
✓ Basic Queries - SELECT with column selection
✓ Filtered Queries - WHERE clauses with comparisons
✓ Pattern Matching - LIKE operator with wildcards
✓ Complex Conditions - AND/OR logic with parentheses
✓ Data Updates - UPDATE with WHERE conditions
✓ Data Deletion - DELETE with conditional logic
✓ Constraint Validation - PRIMARY KEY, UNIQUE, NOT NULL
✓ Schema Management - Table listing and description
✓ File Storage - JSON files with configurable directory

The SQL-JSON engine successfully bridges SQL syntax with JSON file storage,
providing a complete database-like experience with file-based persistence.
    """)


def interactive_example():
    """Run an interactive example session."""
    print_section("Interactive Example")
    
    engine = SQLToJSONEngine()
    
    # Sample SQL statements for user to try
    sample_statements = [
        "CREATE TABLE demo (id INT PRIMARY KEY, name VARCHAR(50), value FLOAT)",
        "INSERT INTO demo VALUES (1, 'Sample', 123.45)",
        "SELECT * FROM demo",
        "UPDATE demo SET value = 999.99 WHERE id = 1",
        "SELECT * FROM demo WHERE value > 500",
        "DELETE FROM demo WHERE id = 1",
        "SHOW TABLES",
        "DESCRIBE demo"
    ]
    
    print("Try these SQL statements:")
    for i, sql in enumerate(sample_statements, 1):
        print(f"{i}. {sql}")
    
    print("\nEnter SQL statements (or 'quit' to exit):")
    
    while True:
        try:
            sql = input("\nSQL> ").strip()
            
            if sql.lower() in ['quit', 'exit', 'q']:
                break
            
            if not sql:
                continue
            
            if sql.lower() == 'show tables':
                tables = engine.list_tables()
                print(f"Tables: {tables}")
                continue
            
            if sql.lower().startswith('describe '):
                table_name = sql[9:].strip()
                schema = engine.describe_table(table_name)
                if schema:
                    print(f"Schema for {table_name}:")
                    print(json.dumps(schema, indent=2))
                else:
                    print(f"Table '{table_name}' not found")
                continue
            
            result = engine.execute_sql(sql)
            print_result(sql, result)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nInteractive session ended.")


if __name__ == "__main__":
    # Run the comprehensive demonstration
    demonstrate_sql_json_engine()
    
    # Optionally run interactive example
    print("\n" + "="*60)
    response = input("Would you like to try the interactive example? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_example()
    
    print("\nExample completed! Check the 'db' directory for generated JSON files.") 