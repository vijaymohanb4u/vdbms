#!/usr/bin/env python3
"""
Test suite for SQL-JSON Engine Integration

This module contains comprehensive tests for the integrated SQL parser
and JSON CRUD system functionality.
"""

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch

from sql_json_engine import SQLToJSONEngine, SQLConsole
from config import config


class TestSQLToJSONEngine(unittest.TestCase):
    """Test the SQL-to-JSON engine functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test databases
        self.test_dir = tempfile.mkdtemp()
        
        # Patch config to use test directory
        self.original_db_dir = config.db_directory
        config.db_directory = self.test_dir
        
        # Create engine instance
        self.engine = SQLToJSONEngine()
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore original config
        config.db_directory = self.original_db_dir
        
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_table_simple(self):
        """Test creating a simple table."""
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))"
        result = self.engine.execute_sql(sql)
        
        self.assertTrue(result["success"])
        self.assertIn("users", self.engine.list_tables())
        
        # Check schema
        schema = self.engine.describe_table("users")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["table_name"], "users")
        self.assertIn("id", schema["columns"])
        self.assertIn("name", schema["columns"])
        self.assertEqual(schema["constraints"]["primary_key"], "id")
    
    def test_create_table_with_constraints(self):
        """Test creating table with various constraints."""
        sql = """CREATE TABLE products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE,
            price FLOAT
        )"""
        result = self.engine.execute_sql(sql)
        
        self.assertTrue(result["success"])
        
        schema = self.engine.describe_table("products")
        self.assertEqual(schema["constraints"]["primary_key"], "id")
        self.assertIn("email", schema["constraints"]["unique"])
        self.assertIn("NOT NULL", schema["columns"]["name"]["constraints"])
        self.assertIn("AUTO_INCREMENT", schema["columns"]["id"]["constraints"])
    
    def test_create_table_already_exists(self):
        """Test creating table that already exists."""
        sql = "CREATE TABLE users (id INT, name VARCHAR(100))"
        
        # Create table first time
        result1 = self.engine.execute_sql(sql)
        self.assertTrue(result1["success"])
        
        # Try to create again
        result2 = self.engine.execute_sql(sql)
        self.assertFalse(result2["success"])
        self.assertIn("already exists", result2["error"])
    
    def test_insert_simple(self):
        """Test simple INSERT operation."""
        # Create table first
        create_sql = "CREATE TABLE users (id INT, name VARCHAR(100))"
        self.engine.execute_sql(create_sql)
        
        # Insert data
        insert_sql = "INSERT INTO users VALUES (1, 'John Doe')"
        result = self.engine.execute_sql(insert_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["inserted_count"], 1)
    
    def test_insert_with_columns(self):
        """Test INSERT with specified columns."""
        # Create table
        create_sql = "CREATE TABLE users (id INT, name VARCHAR(100), email VARCHAR(255))"
        self.engine.execute_sql(create_sql)
        
        # Insert with specific columns
        insert_sql = "INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com')"
        result = self.engine.execute_sql(insert_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["inserted_count"], 1)
    
    def test_insert_multiple_rows(self):
        """Test INSERT with multiple rows."""
        # Create table
        create_sql = "CREATE TABLE users (id INT, name VARCHAR(100))"
        self.engine.execute_sql(create_sql)
        
        # Insert multiple rows
        insert_sql = "INSERT INTO users (name) VALUES ('John'), ('Jane'), ('Bob')"
        result = self.engine.execute_sql(insert_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["inserted_count"], 3)
    
    def test_insert_constraint_violation(self):
        """Test INSERT with constraint violations."""
        # Create table with constraints
        create_sql = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100) NOT NULL)"
        self.engine.execute_sql(create_sql)
        
        # Test NOT NULL violation
        insert_sql = "INSERT INTO users (id) VALUES (1)"
        result = self.engine.execute_sql(insert_sql)
        self.assertFalse(result["success"])
        self.assertIn("cannot be NULL", result["error"])
        
        # Insert valid record
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John')")
        
        # Test PRIMARY KEY violation
        insert_sql = "INSERT INTO users VALUES (1, 'Jane')"
        result = self.engine.execute_sql(insert_sql)
        self.assertFalse(result["success"])
        self.assertIn("primary key", result["error"])
    
    def test_select_all(self):
        """Test SELECT * operation."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100))")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John'), (2, 'Jane')")
        
        # Select all
        select_sql = "SELECT * FROM users"
        result = self.engine.execute_sql(select_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["records"]), 2)
    
    def test_select_specific_columns(self):
        """Test SELECT with specific columns."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100), email VARCHAR(255))")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John', 'john@example.com')")
        
        # Select specific columns
        select_sql = "SELECT name, email FROM users"
        result = self.engine.execute_sql(select_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
        record = result["records"][0]
        self.assertIn("name", record)
        self.assertIn("email", record)
        self.assertNotIn("id", record)
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100), age INT)")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John', 25), (2, 'Jane', 30), (3, 'Bob', 20)")
        
        # Select with WHERE
        select_sql = "SELECT * FROM users WHERE age > 22"
        result = self.engine.execute_sql(select_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)  # John and Jane
    
    def test_select_with_complex_where(self):
        """Test SELECT with complex WHERE clause."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100), age INT)")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John', 25), (2, 'Jane', 30), (3, 'Bob', 20)")
        
        # Complex WHERE with AND
        select_sql = "SELECT * FROM users WHERE age > 20 AND age < 30"
        result = self.engine.execute_sql(select_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)  # Only John
        self.assertEqual(result["records"][0]["name"], "John")
    
    def test_select_with_like(self):
        """Test SELECT with LIKE operator."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100))")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John Doe'), (2, 'Jane Smith'), (3, 'John Wilson')")
        
        # Select with LIKE
        select_sql = "SELECT * FROM users WHERE name LIKE 'John%'"
        result = self.engine.execute_sql(select_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)  # John Doe and John Wilson
    
    def test_update_simple(self):
        """Test simple UPDATE operation."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100), age INT)")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John', 25)")
        
        # Update
        update_sql = "UPDATE users SET age = 26 WHERE id = 1"
        result = self.engine.execute_sql(update_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["updated_count"], 1)
        
        # Verify update
        select_result = self.engine.execute_sql("SELECT * FROM users WHERE id = 1")
        self.assertEqual(select_result["records"][0]["age"], 26)
    
    def test_update_multiple_columns(self):
        """Test UPDATE with multiple columns."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100), age INT)")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John', 25)")
        
        # Update multiple columns
        update_sql = "UPDATE users SET name = 'John Smith', age = 26 WHERE id = 1"
        result = self.engine.execute_sql(update_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["updated_count"], 1)
        
        # Verify update
        select_result = self.engine.execute_sql("SELECT * FROM users WHERE id = 1")
        record = select_result["records"][0]
        self.assertEqual(record["name"], "John Smith")
        self.assertEqual(record["age"], 26)
    
    def test_update_with_constraint_violation(self):
        """Test UPDATE with constraint violation."""
        # Create table with unique constraint
        self.engine.execute_sql("CREATE TABLE users (id INT, email VARCHAR(100) UNIQUE)")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'john@example.com'), (2, 'jane@example.com')")
        
        # Try to update to duplicate email
        update_sql = "UPDATE users SET email = 'john@example.com' WHERE id = 2"
        result = self.engine.execute_sql(update_sql)
        
        self.assertFalse(result["success"])
        self.assertIn("unique", result["error"])
    
    def test_delete_simple(self):
        """Test simple DELETE operation."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, name VARCHAR(100))")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 'John'), (2, 'Jane')")
        
        # Delete
        delete_sql = "DELETE FROM users WHERE id = 1"
        result = self.engine.execute_sql(delete_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_count"], 1)
        
        # Verify deletion
        select_result = self.engine.execute_sql("SELECT * FROM users")
        self.assertEqual(select_result["count"], 1)
        self.assertEqual(select_result["records"][0]["name"], "Jane")
    
    def test_delete_with_complex_where(self):
        """Test DELETE with complex WHERE clause."""
        # Create and populate table
        self.engine.execute_sql("CREATE TABLE users (id INT, age INT)")
        self.engine.execute_sql("INSERT INTO users VALUES (1, 20), (2, 25), (3, 30), (4, 35)")
        
        # Delete with complex WHERE
        delete_sql = "DELETE FROM users WHERE age > 22 AND age < 32"
        result = self.engine.execute_sql(delete_sql)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_count"], 2)  # age 25 and 30
        
        # Verify remaining records
        select_result = self.engine.execute_sql("SELECT * FROM users")
        self.assertEqual(select_result["count"], 2)  # age 20 and 35
    
    def test_table_not_exists_error(self):
        """Test operations on non-existent table."""
        # Try operations on non-existent table
        operations = [
            "INSERT INTO nonexistent VALUES (1, 'test')",
            "SELECT * FROM nonexistent",
            "UPDATE nonexistent SET name = 'test'",
            "DELETE FROM nonexistent"
        ]
        
        for sql in operations:
            result = self.engine.execute_sql(sql)
            self.assertFalse(result["success"])
            self.assertIn("does not exist", result["error"])
    
    def test_invalid_sql(self):
        """Test handling of invalid SQL."""
        invalid_sql = "INVALID SQL STATEMENT"
        result = self.engine.execute_sql(invalid_sql)
        
        self.assertFalse(result["success"])
        self.assertIn("Failed to parse", result["error"])
    
    def test_list_tables(self):
        """Test listing tables."""
        # Initially no tables
        self.assertEqual(len(self.engine.list_tables()), 0)
        
        # Create some tables
        self.engine.execute_sql("CREATE TABLE users (id INT)")
        self.engine.execute_sql("CREATE TABLE products (id INT)")
        
        tables = self.engine.list_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn("users", tables)
        self.assertIn("products", tables)
    
    def test_describe_table(self):
        """Test describing table schema."""
        # Create table
        self.engine.execute_sql("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100) NOT NULL)")
        
        schema = self.engine.describe_table("users")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["table_name"], "users")
        self.assertIn("id", schema["columns"])
        self.assertIn("name", schema["columns"])
        self.assertEqual(schema["constraints"]["primary_key"], "id")
        
        # Non-existent table
        schema = self.engine.describe_table("nonexistent")
        self.assertIsNone(schema)
    
    def test_drop_table(self):
        """Test dropping a table."""
        # Create table
        self.engine.execute_sql("CREATE TABLE users (id INT)")
        self.assertIn("users", self.engine.list_tables())
        
        # Drop table
        result = self.engine.drop_table("users")
        self.assertTrue(result["success"])
        self.assertNotIn("users", self.engine.list_tables())
        
        # Try to drop non-existent table
        result = self.engine.drop_table("nonexistent")
        self.assertFalse(result["success"])
    
    def test_schema_persistence(self):
        """Test that schemas are persisted across engine instances."""
        # Create table
        self.engine.execute_sql("CREATE TABLE users (id INT PRIMARY KEY)")
        
        # Create new engine instance
        new_engine = SQLToJSONEngine()
        
        # Check that schema is loaded
        self.assertIn("users", new_engine.list_tables())
        schema = new_engine.describe_table("users")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["constraints"]["primary_key"], "id")


class TestSQLConsoleIntegration(unittest.TestCase):
    """Test SQL console integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_db_dir = config.db_directory
        config.db_directory = self.test_dir
        self.console = SQLConsole()
    
    def tearDown(self):
        """Clean up test environment."""
        config.db_directory = self.original_db_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_console_creation(self):
        """Test console creation."""
        self.assertIsNotNone(self.console)
        self.assertIsNotNone(self.console.engine)


def run_integration_demo():
    """Run a comprehensive integration demonstration."""
    print("=" * 70)
    print("SQL-JSON ENGINE INTEGRATION DEMONSTRATION")
    print("=" * 70)
    
    # Create temporary directory for demo
    demo_dir = tempfile.mkdtemp()
    original_db_dir = config.db_directory
    config.db_directory = demo_dir
    
    try:
        engine = SQLToJSONEngine()
        
        # Demo scenarios
        scenarios = [
            {
                "name": "Create Tables",
                "statements": [
                    "CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, email VARCHAR(255) UNIQUE)",
                    "CREATE TABLE products (id INT PRIMARY KEY, name VARCHAR(255), price FLOAT, category VARCHAR(50))",
                    "CREATE TABLE orders (order_id INT PRIMARY KEY, user_id INT, product_id INT, quantity INT)"
                ]
            },
            {
                "name": "Insert Data",
                "statements": [
                    "INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')",
                    "INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com'), ('Bob Wilson', 'bob@example.com')",
                    "INSERT INTO products VALUES (1, 'Laptop', 999.99, 'Electronics'), (2, 'Book', 19.99, 'Education')",
                    "INSERT INTO orders VALUES (1, 1, 1, 2), (2, 2, 2, 1)"
                ]
            },
            {
                "name": "Query Data",
                "statements": [
                    "SELECT * FROM users",
                    "SELECT name, email FROM users WHERE name LIKE 'J%'",
                    "SELECT * FROM products WHERE price > 50",
                    "SELECT * FROM orders WHERE quantity > 1"
                ]
            },
            {
                "name": "Update Data",
                "statements": [
                    "UPDATE users SET name = 'John Smith' WHERE email = 'john@example.com'",
                    "UPDATE products SET price = 899.99 WHERE name = 'Laptop'"
                ]
            },
            {
                "name": "Delete Data",
                "statements": [
                    "DELETE FROM orders WHERE quantity = 1",
                    "DELETE FROM products WHERE category = 'Education'"
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name'].upper()}")
            print("-" * len(scenario['name']))
            
            for i, sql in enumerate(scenario['statements'], 1):
                print(f"\n{i}. {sql}")
                result = engine.execute_sql(sql)
                
                if result["success"]:
                    print("   ✓ Success")
                    if "records" in result and "count" in result:
                        if result["records"]:
                            print(f"   Found {result['count']} records:")
                            for record in result["records"][:3]:  # Show first 3 records
                                print(f"     {record}")
                            if result['count'] > 3:
                                print(f"     ... and {result['count'] - 3} more")
                        else:
                            print(f"   No records found")
                    elif "inserted_count" in result:
                        print(f"   Inserted {result['inserted_count']} records")
                    elif "updated_count" in result:
                        print(f"   Updated {result['updated_count']} records")
                    elif "deleted_count" in result:
                        print(f"   Deleted {result['deleted_count']} records")
                    elif "message" in result:
                        print(f"   {result['message']}")
                else:
                    print(f"   ✗ Error: {result['error']}")
        
        # Show final state
        print(f"\nFINAL STATE")
        print("-" * 11)
        tables = engine.list_tables()
        print(f"Tables: {tables}")
        
        for table in tables:
            result = engine.execute_sql(f"SELECT * FROM {table}")
            print(f"{table}: {result['count']} records")
        
    finally:
        # Cleanup
        config.db_directory = original_db_dir
        if os.path.exists(demo_dir):
            shutil.rmtree(demo_dir)


if __name__ == "__main__":
    # Run the integration demonstration first
    run_integration_demo()
    
    # Then run the unit tests
    print("\n" + "="*70)
    print("Running Integration Tests")
    print("="*70)
    unittest.main(verbosity=2) 