import unittest
import os
import tempfile
import json
import shutil
from json_crud import JSONDatabase, insert_record, read_records, update_record, delete_record, list_databases, get_database_info
from config import config


class TestJSONDatabase(unittest.TestCase):
    """Test cases for JSONDatabase class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_db_dir = config.db_directory
        
        # Set config to use test directory
        config.set('database.directory', self.test_dir)
        config.ensure_db_directory()
        
        self.db = JSONDatabase("test_db")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Restore original config
        config.set('database.directory', self.original_db_dir)
        
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_insert_record(self):
        """Test inserting records."""
        # Test basic insert
        record = {"name": "John Doe", "age": 30, "email": "john@example.com"}
        record_id = self.db.insert(record)
        
        self.assertIsNotNone(record_id)
        self.assertIn('id', record)
        self.assertIn('created_at', record)
        self.assertIn('updated_at', record)
        
        # Test insert without auto ID
        record2 = {"id": "custom_id", "name": "Jane Doe", "age": 25}
        record_id2 = self.db.insert(record2, auto_id=False)
        self.assertEqual(record_id2, "custom_id")
        
        # Test invalid record types
        with self.assertRaises(ValueError):
            self.db.insert("not a dict")
        
        with self.assertRaises(ValueError):
            self.db.insert({})
    
    def test_read_records(self):
        """Test reading records."""
        # Insert test data
        record1 = {"name": "Alice", "department": "Engineering", "salary": 75000}
        record2 = {"name": "Bob", "department": "Marketing", "salary": 65000}
        record3 = {"name": "Charlie", "department": "Engineering", "salary": 80000}
        
        id1 = self.db.insert(record1)
        id2 = self.db.insert(record2)
        id3 = self.db.insert(record3)
        
        # Test read all records
        all_records = self.db.read()
        self.assertEqual(len(all_records), 3)
        
        # Test read specific record
        specific_record = self.db.read(record_id=id1)
        self.assertEqual(specific_record['name'], "Alice")
        
        # Test read with filters
        engineering_records = self.db.read(filters={"department": "Engineering"})
        self.assertEqual(len(engineering_records), 2)
        
        # Test read non-existent record
        with self.assertRaises(ValueError):
            self.db.read(record_id="non_existent_id")
    
    def test_update_record(self):
        """Test updating records."""
        # Insert test record
        record = {"name": "Test User", "status": "active", "score": 100}
        record_id = self.db.insert(record)
        
        # Test basic update
        updates = {"status": "inactive", "score": 150}
        updated_record = self.db.update(record_id, updates)
        
        self.assertEqual(updated_record['status'], "inactive")
        self.assertEqual(updated_record['score'], 150)
        self.assertEqual(updated_record['name'], "Test User")  # Unchanged field
        self.assertNotEqual(updated_record['created_at'], updated_record['updated_at'])
        
        # Test update non-existent record
        with self.assertRaises(ValueError):
            self.db.update("non_existent_id", {"field": "value"})
        
        # Test invalid updates
        with self.assertRaises(ValueError):
            self.db.update(record_id, "not a dict")
        
        with self.assertRaises(ValueError):
            self.db.update(record_id, {})
        
        with self.assertRaises(ValueError):
            self.db.update("", {"field": "value"})
    
    def test_delete_record(self):
        """Test deleting records."""
        # Insert test records
        record1 = {"name": "To Delete", "value": 1}
        record2 = {"name": "To Keep", "value": 2}
        
        id1 = self.db.insert(record1)
        id2 = self.db.insert(record2)
        
        # Test successful delete
        result = self.db.delete(id1)
        self.assertTrue(result)
        
        # Verify record is deleted
        all_records = self.db.read()
        self.assertEqual(len(all_records), 1)
        self.assertEqual(all_records[0]['name'], "To Keep")
        
        # Test delete non-existent record
        result = self.db.delete("non_existent_id")
        self.assertFalse(result)
        
        # Test invalid record ID
        with self.assertRaises(ValueError):
            self.db.delete("")
    
    def test_count_records(self):
        """Test counting records."""
        # Test empty database
        self.assertEqual(self.db.count(), 0)
        
        # Insert test data
        self.db.insert({"category": "A", "value": 1})
        self.db.insert({"category": "B", "value": 2})
        self.db.insert({"category": "A", "value": 3})
        
        # Test count all
        self.assertEqual(self.db.count(), 3)
        
        # Test count with filters
        self.assertEqual(self.db.count(filters={"category": "A"}), 2)
        self.assertEqual(self.db.count(filters={"category": "B"}), 1)
        self.assertEqual(self.db.count(filters={"category": "C"}), 0)
    
    def test_clear_database(self):
        """Test clearing the database."""
        # Insert test data
        self.db.insert({"test": "data1"})
        self.db.insert({"test": "data2"})
        
        self.assertEqual(self.db.count(), 2)
        
        # Clear database
        self.db.clear()
        self.assertEqual(self.db.count(), 0)
    
    def test_database_properties(self):
        """Test database path properties."""
        # Test that database is created in the configured directory
        self.assertTrue(self.db.database_path.startswith(self.test_dir))
        self.assertEqual(self.db.database_name, "test_db.json")
    
    def test_file_operations_error_handling(self):
        """Test error handling for file operations."""
        # Test with invalid file path (Windows compatible)
        original_dir = config.db_directory
        config.set('database.directory', "Z:\\invalid\\path")
        
        with self.assertRaises(IOError):
            invalid_db = JSONDatabase("test")
        
        # Restore config
        config.set('database.directory', original_dir)


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_db_dir = config.db_directory
        
        # Set config to use test directory
        config.set('database.directory', self.test_dir)
        config.ensure_db_directory()
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original config
        config.set('database.directory', self.original_db_dir)
        
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_convenience_functions(self):
        """Test all convenience functions."""
        # Test insert
        record_id = insert_record("test_convenience", {"name": "Test", "value": 42})
        self.assertIsNotNone(record_id)
        
        # Test read all
        all_records = read_records("test_convenience")
        self.assertEqual(len(all_records), 1)
        
        # Test read specific
        specific_record = read_records("test_convenience", record_id=record_id)
        self.assertEqual(specific_record['name'], "Test")
        
        # Test update
        updated_record = update_record("test_convenience", record_id, {"value": 100})
        self.assertEqual(updated_record['value'], 100)
        
        # Test delete
        result = delete_record("test_convenience", record_id)
        self.assertTrue(result)
        
        # Verify deletion
        all_records = read_records("test_convenience")
        self.assertEqual(len(all_records), 0)
    
    def test_list_databases(self):
        """Test listing databases."""
        # Initially no databases
        databases = list_databases()
        initial_count = len(databases)
        
        # Create some databases
        insert_record("db1", {"test": "data1"})
        insert_record("db2", {"test": "data2"})
        insert_record("db3", {"test": "data3"})
        
        # Check that databases are listed
        databases = list_databases()
        self.assertEqual(len(databases), initial_count + 3)
        self.assertIn("db1.json", databases)
        self.assertIn("db2.json", databases)
        self.assertIn("db3.json", databases)
    
    def test_get_database_info(self):
        """Test getting database information."""
        # Test non-existent database with a unique name
        info = get_database_info("definitely_nonexistent_unique_name")
        self.assertFalse(info["exists"])
        
        # Create a database and test info
        insert_record("info_test", {"name": "Test", "value": 123})
        insert_record("info_test", {"name": "Test2", "value": 456})
        
        info = get_database_info("info_test")
        self.assertTrue(info["exists"])
        self.assertEqual(info["filename"], "info_test.json")
        self.assertEqual(info["record_count"], 2)
        self.assertGreater(info["file_size_bytes"], 0)
        self.assertIsNotNone(info["created"])
        self.assertIsNotNone(info["modified"])


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_db_dir = config.db_directory
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original config
        config.set('database.directory', self.original_db_dir)
        
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_config_directory_change(self):
        """Test changing database directory via config."""
        # Change directory
        config.set('database.directory', self.test_dir)
        
        # Create database - should be in new directory
        db = JSONDatabase("config_test")
        self.assertTrue(db.database_path.startswith(self.test_dir))
        
        # Insert data
        db.insert({"test": "config_data"})
        
        # Verify file exists in correct location
        expected_path = os.path.join(self.test_dir, "config_test.json")
        self.assertTrue(os.path.exists(expected_path))
    
    def test_auto_directory_creation(self):
        """Test automatic directory creation."""
        new_dir = os.path.join(self.test_dir, "auto_created")
        config.set('database.directory', new_dir)
        
        # Directory shouldn't exist yet
        self.assertFalse(os.path.exists(new_dir))
        
        # Creating database should create directory
        db = JSONDatabase("auto_test")
        self.assertTrue(os.path.exists(new_dir))


def run_demo():
    """Demonstrate the JSON CRUD operations with configuration."""
    print("=== JSON CRUD Operations Demo (with Configuration) ===\n")
    
    # Show current configuration
    print(f"Database directory: {config.db_directory}")
    print(f"Auto-create directory: {config.auto_create_directory}")
    print(f"Default extension: {config.default_extension}")
    print(f"Pretty print: {config.pretty_print}")
    
    # Create a demo database
    db = JSONDatabase("demo_users")
    
    try:
        print(f"\nDatabase file location: {db.database_path}")
        print("\n1. Inserting records...")
        
        # Insert some sample users
        users = [
            {"name": "Alice Johnson", "email": "alice@example.com", "department": "Engineering", "salary": 75000},
            {"name": "Bob Smith", "email": "bob@example.com", "department": "Marketing", "salary": 65000},
            {"name": "Charlie Brown", "email": "charlie@example.com", "department": "Engineering", "salary": 80000},
            {"name": "Diana Prince", "email": "diana@example.com", "department": "HR", "salary": 70000}
        ]
        
        user_ids = []
        for user in users:
            user_id = db.insert(user)
            user_ids.append(user_id)
            print(f"   Inserted user: {user['name']} (ID: {user_id})")
        
        print(f"\n2. Reading all records (Total: {db.count()})...")
        all_users = db.read()
        for user in all_users:
            print(f"   {user['name']} - {user['department']} - ${user['salary']}")
        
        print("\n3. Reading with filters (Engineering department)...")
        eng_users = db.read(filters={"department": "Engineering"})
        for user in eng_users:
            print(f"   {user['name']} - ${user['salary']}")
        
        print(f"\n4. Reading specific record (ID: {user_ids[0]})...")
        specific_user = db.read(record_id=user_ids[0])
        print(f"   {specific_user['name']} - {specific_user['email']}")
        
        print(f"\n5. Updating record (ID: {user_ids[1]})...")
        updated_user = db.update(user_ids[1], {"salary": 70000, "department": "Sales"})
        print(f"   Updated: {updated_user['name']} - {updated_user['department']} - ${updated_user['salary']}")
        
        print(f"\n6. Deleting record (ID: {user_ids[2]})...")
        deleted = db.delete(user_ids[2])
        print(f"   Deleted: {deleted}")
        print(f"   Remaining records: {db.count()}")
        
        print("\n7. Final state of database...")
        final_users = db.read()
        for user in final_users:
            print(f"   {user['name']} - {user['department']} - ${user['salary']}")
        
        print("\n8. Database management functions...")
        databases = list_databases()
        print(f"   Available databases: {databases}")
        
        db_info = get_database_info("demo_users")
        print(f"   Database info: {db_info['record_count']} records, {db_info['file_size_bytes']} bytes")
        
        print("\n9. Testing error handling...")
        try:
            db.read(record_id="non_existent_id")
        except ValueError as e:
            print(f"   Caught expected error: {e}")
        
        try:
            db.update("", {"field": "value"})
        except ValueError as e:
            print(f"   Caught expected error: {e}")
        
        print("\n10. Clearing database...")
        db.clear()
        print(f"   Records after clear: {db.count()}")
        
    except Exception as e:
        print(f"Error during demo: {e}")
    
    print("\n=== Demo completed ===")


if __name__ == "__main__":
    # Run the demo
    run_demo()
    
    print("\n" + "="*50)
    print("Running unit tests...")
    print("="*50)
    
    # Run unit tests
    unittest.main(verbosity=2) 