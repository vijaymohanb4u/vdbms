# JSON CRUD Operations

A simple, lightweight Python library for performing CRUD (Create, Read, Update, Delete) operations on JSON files, treating them as database tables. Now with **configuration-based file management** for organized database storage.

## Features

- **Complete CRUD Operations**: Insert, read, update, and delete records
- **Configuration Management**: Centralized settings via `settings.json`
- **Organized File Storage**: All database files stored in configurable directory (default: `db/`)
- **Automatic ID Generation**: UUID-based unique identifiers
- **Timestamp Tracking**: Automatic `created_at` and `updated_at` timestamps
- **Filtering Support**: Query records with custom filters
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Type Safety**: Full type hints for better IDE support
- **Convenience Functions**: Simple functions for quick operations
- **Database Management**: List, inspect, and manage multiple databases

## Installation

No external dependencies required! Just copy the files to your project.

```bash
# Copy these files to your project:
# - json_crud.py (main CRUD operations)
# - config.py (configuration management)
# - settings.json (configuration file)
```

## Configuration

The system uses a `settings.json` file for configuration:

```json
{
  "database": {
    "directory": "db",
    "auto_create_directory": true,
    "default_file_extension": ".json",
    "backup_enabled": false,
    "backup_directory": "db/backups"
  },
  "logging": {
    "enabled": false,
    "level": "INFO",
    "file": "db/crud.log"
  },
  "performance": {
    "cache_enabled": false,
    "max_file_size_mb": 10,
    "pretty_print": true
  }
}
```

### Key Configuration Options

- **`database.directory`**: Where database files are stored (default: `"db"`)
- **`database.auto_create_directory`**: Automatically create the database directory
- **`database.default_file_extension`**: File extension for database files
- **`performance.pretty_print`**: Format JSON with indentation for readability

## Quick Start

### Using the JSONDatabase Class

```python
from json_crud import JSONDatabase

# Create a database instance (file will be stored in db/users.json)
db = JSONDatabase("users")

# Insert a record
user_id = db.insert({
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

# Read all records
all_users = db.read()

# Read a specific record
user = db.read(record_id=user_id)

# Read with filters
adults = db.read(filters={"age": 30})

# Update a record
updated_user = db.update(user_id, {"age": 31})

# Delete a record
deleted = db.delete(user_id)

# Count records
total_users = db.count()

# Get database info
print(f"Database stored at: {db.database_path}")
```

### Using Convenience Functions

```python
from json_crud import insert_record, read_records, update_record, delete_record

# Insert (creates db/users.json)
user_id = insert_record("users", {"name": "Jane", "age": 25})

# Read
users = read_records("users")
specific_user = read_records("users", record_id=user_id)

# Update
updated = update_record("users", user_id, {"age": 26})

# Delete
deleted = delete_record("users", user_id)
```

### Database Management

```python
from json_crud import list_databases, get_database_info

# List all database files
databases = list_databases()
print("Available databases:", databases)

# Get detailed information about a database
info = get_database_info("users")
print(f"Records: {info['record_count']}")
print(f"File size: {info['file_size_bytes']} bytes")
print(f"Created: {info['created']}")
```

### Configuration Management

```python
from config import config

# View current configuration
print(f"Database directory: {config.db_directory}")
print(f"Pretty print: {config.pretty_print}")

# Change configuration
config.set('database.directory', 'my_databases')
config.set('performance.pretty_print', False)

# Get database path
path = config.get_db_path("example")  # Returns: my_databases/example.json
```

## File Structure

With the configuration system, your project structure will look like:

```
your_project/
├── json_crud.py          # Main CRUD operations
├── config.py             # Configuration management
├── settings.json         # Configuration file
├── example_usage.py      # Usage examples
├── test_json_crud.py     # Test suite
└── db/                   # Database files directory
    ├── users.json
    ├── products.json
    ├── orders.json
    └── ...
```

## API Reference

### JSONDatabase Class

#### Constructor
```python
JSONDatabase(file_path: str)
```
Creates a new database instance. The file will be stored in the configured database directory.

- **file_path**: Database filename (without path, e.g., "users" or "users.json")

#### Methods

##### `insert(record: Dict[str, Any], auto_id: bool = True) -> str`
Insert a new record into the database.

##### `read(record_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]`
Read records from the database.

##### `update(record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]`
Update an existing record.

##### `delete(record_id: str) -> bool`
Delete a record from the database.

##### `count(filters: Optional[Dict[str, Any]] = None) -> int`
Count records in the database.

##### `clear() -> None`
Remove all records from the database.

#### Properties

##### `database_path -> str`
Get the full path to the database file.

##### `database_name -> str`
Get the database filename without path.

### Convenience Functions

#### `insert_record(file_path: str, record: Dict[str, Any], auto_id: bool = True) -> str`
Insert a record into a database file.

#### `read_records(file_path: str, record_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None)`
Read records from a database file.

#### `update_record(file_path: str, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]`
Update a record in a database file.

#### `delete_record(file_path: str, record_id: str) -> bool`
Delete a record from a database file.

#### `list_databases() -> List[str]`
List all database files in the configured directory.

#### `get_database_info(file_path: str) -> Dict[str, Any]`
Get detailed information about a database file.

### Configuration Class

#### `config.get(key: str, default: Any = None) -> Any`
Get configuration value using dot notation (e.g., `"database.directory"`).

#### `config.set(key: str, value: Any) -> None`
Set configuration value using dot notation.

#### `config.get_db_path(filename: str) -> str`
Get full path for a database file in the configured directory.

## Examples

### Basic CRUD Operations

```python
from json_crud import JSONDatabase

# Initialize database (stored in db/products.json)
db = JSONDatabase("products")

# Create
product_id = db.insert({
    "name": "Laptop",
    "price": 999.99,
    "category": "Electronics",
    "in_stock": True
})

# Read
product = db.read(record_id=product_id)
all_products = db.read()
electronics = db.read(filters={"category": "Electronics"})

# Update
updated_product = db.update(product_id, {
    "price": 899.99,
    "on_sale": True
})

# Delete
deleted = db.delete(product_id)
```

### Multiple Databases

```python
from json_crud import JSONDatabase, list_databases

# Create multiple databases
users_db = JSONDatabase("users")
orders_db = JSONDatabase("orders")
products_db = JSONDatabase("products")

# Add data to each
users_db.insert({"name": "Alice", "email": "alice@example.com"})
orders_db.insert({"user": "alice", "total": 150.00})
products_db.insert({"name": "Widget", "price": 25.99})

# List all databases
databases = list_databases()
print("Available databases:", databases)
# Output: ['orders.json', 'products.json', 'users.json']
```

### Configuration Changes

```python
from config import config
from json_crud import JSONDatabase

# Change database directory
config.set('database.directory', 'data')

# Now databases will be stored in data/ instead of db/
db = JSONDatabase("test")  # Creates data/test.json

# Change formatting
config.set('performance.pretty_print', False)  # Compact JSON
```

## File Format

Database files are stored as JSON arrays in the configured directory:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "created_at": "2023-12-07T10:30:00.123456",
    "updated_at": "2023-12-07T10:30:00.123456"
  }
]
```

## Running Tests

Run the comprehensive test suite:

```bash
python test_json_crud.py
```

Run examples:

```bash
python example_usage.py
```

## Migration from Previous Version

If you have existing JSON database files, simply:

1. Create a `db/` directory
2. Move your `.json` files into the `db/` directory
3. Update your code to use filenames without paths:
   ```python
   # Old way
   db = JSONDatabase("path/to/users.json")
   
   # New way
   db = JSONDatabase("users")  # Will use db/users.json
   ```

## Error Handling

The library provides comprehensive error handling:

- **ValueError**: Invalid input data, empty records, missing record IDs
- **IOError**: File operation errors (permissions, disk space, etc.)
- **Configuration errors**: Invalid settings, missing directories

## Limitations

- **File-based**: Not suitable for high-concurrency applications
- **Memory usage**: Entire file is loaded into memory for operations
- **No indexing**: Linear search for filtering operations
- **No transactions**: No atomic operations across multiple records
- **No schema validation**: Records can have any structure

## Use Cases

Perfect for:
- Small to medium datasets (< 10,000 records)
- Configuration storage
- Prototyping and development
- Simple data persistence
- Educational projects
- Applications where a full database is overkill
- Multi-tenant applications (separate database per tenant)

## Contributing

Feel free to submit issues, feature requests, or pull requests!

## License

This project is released into the public domain. Use it however you like! 