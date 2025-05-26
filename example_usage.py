#!/usr/bin/env python3
"""
Example usage of JSON CRUD operations with configuration system.

This file demonstrates basic usage patterns for the JSON database CRUD operations
with the new configuration-based file management.
"""

from json_crud import JSONDatabase, insert_record, read_records, update_record, delete_record, list_databases, get_database_info
from config import config


def basic_usage_example():
    """Demonstrate basic usage patterns."""
    print("=== Basic Usage Example ===\n")
    
    print(f"Database directory: {config.db_directory}")
    print(f"Files will be stored in: {config.db_directory}/\n")
    
    # Method 1: Using the JSONDatabase class
    print("1. Using JSONDatabase class:")
    db = JSONDatabase("employees")  # Will create db/employees.json
    
    print(f"   Database file: {db.database_path}")
    
    # Insert records
    emp1_id = db.insert({"name": "John Doe", "position": "Developer", "salary": 75000})
    emp2_id = db.insert({"name": "Jane Smith", "position": "Designer", "salary": 70000})
    
    print(f"   Inserted employees with IDs: {emp1_id}, {emp2_id}")
    
    # Read all records
    all_employees = db.read()
    print(f"   Total employees: {len(all_employees)}")
    
    # Read with filters
    developers = db.read(filters={"position": "Developer"})
    print(f"   Developers: {len(developers)}")
    
    # Update a record
    updated_emp = db.update(emp1_id, {"salary": 80000})
    print(f"   Updated {updated_emp['name']}'s salary to ${updated_emp['salary']}")
    
    # Delete a record
    deleted = db.delete(emp2_id)
    print(f"   Deleted employee: {deleted}")
    
    # Clean up
    db.clear()
    
    print("\n" + "-"*50 + "\n")
    
    # Method 2: Using convenience functions
    print("2. Using convenience functions:")
    
    # Insert using convenience function
    product_id = insert_record("products", {  # Will create db/products.json
        "name": "Laptop",
        "category": "Electronics",
        "price": 999.99,
        "in_stock": True
    })
    print(f"   Inserted product with ID: {product_id}")
    
    # Read using convenience function
    all_products = read_records("products")
    print(f"   Products in database: {len(all_products)}")
    
    # Update using convenience function
    updated_product = update_record("products", product_id, {
        "price": 899.99,
        "on_sale": True
    })
    print(f"   Updated product price to ${updated_product['price']}")
    
    # Delete using convenience function
    deleted = delete_record("products", product_id)
    print(f"   Deleted product: {deleted}")


def database_management_example():
    """Demonstrate database management functions."""
    print("=== Database Management Example ===\n")
    
    # Create multiple databases
    print("1. Creating multiple databases:")
    
    # Create users database
    insert_record("users", {"name": "Alice", "role": "admin"})
    insert_record("users", {"name": "Bob", "role": "user"})
    
    # Create orders database
    insert_record("orders", {"user_id": "alice", "amount": 150.00, "status": "completed"})
    insert_record("orders", {"user_id": "bob", "amount": 75.50, "status": "pending"})
    
    # Create products database
    insert_record("products", {"name": "Widget", "price": 25.99, "stock": 100})
    
    print("   Created users, orders, and products databases")
    
    # List all databases
    print("\n2. Listing all databases:")
    databases = list_databases()
    for db_name in databases:
        print(f"   - {db_name}")
    
    # Get information about each database
    print("\n3. Database information:")
    for db_name in databases:
        # Remove .json extension for the function call
        db_name_clean = db_name.replace('.json', '')
        info = get_database_info(db_name_clean)
        if info["exists"]:
            print(f"   {db_name}:")
            print(f"     Records: {info['record_count']}")
            print(f"     Size: {info['file_size_bytes']} bytes")
            print(f"     Created: {info['created']}")
            print(f"     Modified: {info['modified']}")
        else:
            print(f"   {db_name}: Error - {info.get('error', 'Unknown error')}")


def configuration_example():
    """Demonstrate configuration management."""
    print("=== Configuration Example ===\n")
    
    # Show current configuration
    print("1. Current configuration:")
    print(f"   Database directory: {config.db_directory}")
    print(f"   Auto-create directory: {config.auto_create_directory}")
    print(f"   Default extension: {config.default_extension}")
    print(f"   Pretty print JSON: {config.pretty_print}")
    
    # Demonstrate changing configuration
    print("\n2. Changing configuration:")
    original_pretty = config.pretty_print
    
    # Turn off pretty printing
    config.set('performance.pretty_print', False)
    print(f"   Set pretty print to: {config.pretty_print}")
    
    # Create a database with compact JSON
    db = JSONDatabase("compact_test")
    db.insert({"test": "compact", "data": [1, 2, 3]})
    
    # Restore pretty printing
    config.set('performance.pretty_print', original_pretty)
    print(f"   Restored pretty print to: {config.pretty_print}")
    
    # Show how to get database path
    print(f"\n3. Database path resolution:")
    test_path = config.get_db_path("example")
    print(f"   'example' resolves to: {test_path}")
    
    test_path2 = config.get_db_path("example.json")
    print(f"   'example.json' resolves to: {test_path2}")


def error_handling_example():
    """Demonstrate error handling."""
    print("=== Error Handling Example ===\n")
    
    db = JSONDatabase("test_errors")
    
    try:
        # Try to insert invalid data
        db.insert("not a dictionary")
    except ValueError as e:
        print(f"Caught ValueError: {e}")
    
    try:
        # Try to read non-existent record
        db.read(record_id="non_existent")
    except ValueError as e:
        print(f"Caught ValueError: {e}")
    
    try:
        # Try to update with invalid data
        db.update("some_id", "not a dictionary")
    except ValueError as e:
        print(f"Caught ValueError: {e}")


def advanced_usage_example():
    """Demonstrate advanced usage patterns."""
    print("=== Advanced Usage Example ===\n")
    
    db = JSONDatabase("library")
    
    # Insert books with custom IDs
    books = [
        {"id": "book_001", "title": "Python Programming", "author": "John Author", "genre": "Technology", "year": 2023},
        {"id": "book_002", "title": "Data Science Handbook", "author": "Jane Expert", "genre": "Technology", "year": 2022},
        {"id": "book_003", "title": "Mystery Novel", "author": "A. Mystery", "genre": "Fiction", "year": 2021},
    ]
    
    for book in books:
        db.insert(book, auto_id=False)  # Use custom IDs
    
    print(f"Inserted {db.count()} books")
    
    # Complex filtering
    tech_books = db.read(filters={"genre": "Technology"})
    print(f"Technology books: {len(tech_books)}")
    
    recent_books = []
    all_books = db.read()
    for book in all_books:
        if book.get("year", 0) >= 2022:
            recent_books.append(book)
    
    print(f"Recent books (2022+): {len(recent_books)}")
    
    # Batch updates (update multiple records)
    for book in all_books:
        if book.get("genre") == "Technology":
            db.update(book["id"], {"category": "Technical", "available": True})
    
    # Count with filters
    available_count = db.count(filters={"available": True})
    print(f"Available books: {available_count}")
    
    # Show database file location
    print(f"Library database stored at: {db.database_path}")


def cleanup_example():
    """Demonstrate cleanup operations."""
    print("=== Cleanup Example ===\n")
    
    # Show all databases before cleanup
    print("Databases before cleanup:")
    databases = list_databases()
    for db_name in databases:
        print(f"   - {db_name}")
    
    # Clear specific databases
    print("\nClearing specific databases:")
    for db_name in ["users", "orders", "products", "compact_test", "test_errors", "library"]:
        try:
            db = JSONDatabase(db_name)
            db.clear()
            print(f"   Cleared {db_name}")
        except Exception as e:
            print(f"   Error clearing {db_name}: {e}")
    
    # Show databases after cleanup
    print("\nDatabases after cleanup:")
    databases = list_databases()
    for db_name in databases:
        db_name_clean = db_name.replace('.json', '')
        info = get_database_info(db_name_clean)
        print(f"   - {db_name} ({info.get('record_count', 0)} records)")


if __name__ == "__main__":
    basic_usage_example()
    database_management_example()
    configuration_example()
    error_handling_example()
    advanced_usage_example()
    cleanup_example()
    
    print("\n=== All examples completed successfully! ===")
    print(f"Check the '{config.db_directory}' directory to see the created database files.") 