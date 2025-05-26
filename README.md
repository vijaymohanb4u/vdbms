# VDBMS - SQL-to-JSON Database Engine

A lightweight, file-based database management system that provides a complete SQL interface for JSON-based database operations. Execute standard SQL statements on JSON files as if they were database tables, with full schema management, constraint validation, and an interactive SQL console.

## 🚀 Key Features

### Complete SQL Database Interface
- **Full SQL Support**: `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE` statements
- **Schema Management**: Persistent table schemas with data type definitions
- **Constraint Validation**: `PRIMARY KEY`, `UNIQUE`, `NOT NULL`, `AUTO_INCREMENT` support
- **Complex Queries**: WHERE clauses with `AND`/`OR` logic, parentheses grouping, and `LIKE` pattern matching
- **Interactive SQL Console**: Command-line interface for executing SQL statements

### JSON-Based Storage
- **Human-Readable**: All data stored as formatted JSON files
- **File-Based**: No database server required - just files on disk
- **Configurable Storage**: Organized database directory structure
- **Schema Registry**: Persistent schema storage in `_schemas.json`

### Direct JSON CRUD Operations
- **JSONDatabase Class**: Direct programmatic access to JSON files
- **Automatic ID Generation**: UUID-based unique identifiers
- **Timestamp Tracking**: Automatic `created_at` and `updated_at` timestamps
- **Filtering Support**: Query records with custom filters
- **Convenience Functions**: Simple functions for quick operations

## 📦 Installation

### Requirements
```bash
pip install ply>=3.11
```

### Quick Setup
```bash
# Clone or download the project
git clone <repository-url>
cd vdbms

# Install dependencies
pip install -r requirements.txt

# Run the interactive SQL console
python sql_json_engine.py
```

## 🎯 Quick Start

### Interactive SQL Console

```bash
python sql_json_engine.py
```

```sql
SQL> CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    age INT
);

SQL> INSERT INTO users (name, email, age) VALUES 
    ('John Doe', 'john@example.com', 30),
    ('Jane Smith', 'jane@example.com', 25);

SQL> SELECT * FROM users WHERE age > 25;

SQL> UPDATE users SET age = 31 WHERE name = 'John Doe';

SQL> DELETE FROM users WHERE age < 18;
```

### Programmatic SQL Interface

```python
from sql_json_engine import SQLToJSONEngine

# Create engine instance
engine = SQLToJSONEngine()

# Create table
result = engine.execute_sql("""
    CREATE TABLE products (
        id INT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price FLOAT,
        category VARCHAR(50)
    )
""")

# Insert data
result = engine.execute_sql("""
    INSERT INTO products VALUES 
    (1, 'Laptop', 999.99, 'Electronics'),
    (2, 'Book', 29.99, 'Education')
""")

# Query data
result = engine.execute_sql("SELECT * FROM products WHERE price > 50")
print(f"Found {result['count']} products")
for product in result['records']:
    print(f"- {product['name']}: ${product['price']}")
```

### Direct JSON Operations

```python
from json_crud import JSONDatabase

# Create database instance (stored in db/inventory.json)
db = JSONDatabase("inventory")

# Insert records
item_id = db.insert({
    "name": "Widget",
    "quantity": 100,
    "price": 25.99
})

# Query with filters
expensive_items = db.read(filters={"price": lambda x: x > 20})

# Update records
db.update(item_id, {"quantity": 95})

# Delete records
db.delete(item_id)
```

## 🏗️ Project Structure

```
vdbms/
├── sql_json_engine.py         # Main SQL-to-JSON integration engine
├── sql_parser.py              # PLY-based SQL parser with AST generation
├── json_crud.py               # JSON CRUD operations with validation
├── config.py                  # Configuration management system
├── settings.json              # Configuration file
├── test_sql_json_engine.py    # Integration tests
├── test_sql_parser.py         # SQL parser tests
├── test_json_crud.py          # JSON CRUD tests
├── example_usage.py           # Usage examples
├── requirements.txt           # Dependencies
└── db/                        # Database files directory
    ├── _schemas.json          # Table schema registry
    ├── users.json             # Example table files
    ├── products.json
    └── orders.json
```

## 📊 Supported SQL Features

### Data Definition Language (DDL)
```sql
-- Create tables with constraints
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    age INT,
    created_at TIMESTAMP
);

-- Show table information
SHOW TABLES;
DESCRIBE users;
```

### Data Manipulation Language (DML)
```sql
-- Insert single or multiple records
INSERT INTO users (name, email, age) VALUES ('John', 'john@example.com', 30);
INSERT INTO users (name, email) VALUES ('Jane', 'jane@example.com'), ('Bob', 'bob@example.com');

-- Select with complex conditions
SELECT name, email FROM users WHERE age > 18 AND email LIKE '%@example.com';
SELECT * FROM users WHERE (age > 20 AND age < 40) OR name = 'Admin';

-- Update with conditions
UPDATE users SET age = 31, email = 'newemail@example.com' WHERE id = 1;

-- Delete with conditions
DELETE FROM users WHERE age < 18 OR name LIKE 'test%';
```

### Supported Data Types
- `INT`, `INTEGER`
- `VARCHAR(size)`, `TEXT`
- `FLOAT`, `DOUBLE`
- `BOOLEAN`
- `DATE`, `DATETIME`, `TIMESTAMP`

### Supported Constraints
- `PRIMARY KEY` - Unique identifier for records
- `UNIQUE` - Ensure column values are unique
- `NOT NULL` - Prevent null values
- `AUTO_INCREMENT` - Automatic ID generation

### Supported Operators
- **Comparison**: `=`, `!=`, `<>`, `<`, `>`, `<=`, `>=`
- **Pattern Matching**: `LIKE` with `%` and `_` wildcards
- **Logical**: `AND`, `OR`, `NOT`
- **Grouping**: Parentheses `()` for complex conditions

## ⚙️ Configuration

The system uses `settings.json` for configuration:

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

### Configuration Management
```python
from config import config

# View current settings
print(f"Database directory: {config.db_directory}")
print(f"Pretty print JSON: {config.pretty_print}")

# Change settings
config.set('database.directory', 'my_data')
config.set('performance.pretty_print', False)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test SQL-JSON integration
python test_sql_json_engine.py

# Test SQL parser
python test_sql_parser.py

# Test JSON CRUD operations
python test_json_crud.py

# Run all tests
python -m unittest discover -s . -p "test_*.py"
```

## 📝 Examples

### E-commerce Database Example

```sql
-- Create product catalog
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    category VARCHAR(100),
    stock_quantity INT,
    created_at TIMESTAMP
);

-- Create customer table
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    address TEXT
);

-- Create orders table
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    total_amount FLOAT,
    order_date TIMESTAMP
);

-- Insert sample data
INSERT INTO products (name, price, category, stock_quantity) VALUES
    ('Laptop Pro', 1299.99, 'Electronics', 50),
    ('Wireless Mouse', 29.99, 'Electronics', 200),
    ('Office Chair', 199.99, 'Furniture', 25);

INSERT INTO customers (name, email, phone) VALUES
    ('John Doe', 'john@example.com', '555-0123'),
    ('Jane Smith', 'jane@example.com', '555-0456');

-- Query examples
SELECT p.name, p.price, p.stock_quantity 
FROM products p 
WHERE p.category = 'Electronics' AND p.price < 100;

SELECT c.name, c.email 
FROM customers c 
WHERE c.email LIKE '%@example.com';

-- Update inventory
UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = 1;

-- Clean up old test data
DELETE FROM orders WHERE order_date < '2023-01-01';
```

## 🎯 Use Cases

### Perfect For:
- **Prototyping**: Quick database setup without installing a full RDBMS
- **Small to Medium Applications**: Projects with < 10,000 records per table
- **Educational Projects**: Learning SQL concepts with visible, editable data files
- **Development/Testing**: Local development where you want to inspect data files directly
- **Configuration Storage**: Structured configuration data with SQL query capabilities
- **Embedded Applications**: Applications that need a database but can't install a server
- **Data Analysis Scripts**: Quick data manipulation with familiar SQL syntax

### Not Suitable For:
- **High-Concurrency Applications**: File-based storage doesn't support concurrent writes
- **Large Datasets**: Entire files are loaded into memory
- **Production Systems**: Lacks advanced features like indexing, transactions, replication
- **Real-time Applications**: No optimization for high-performance queries

## 🔧 API Reference

### SQLToJSONEngine Class

```python
from sql_json_engine import SQLToJSONEngine

engine = SQLToJSONEngine()

# Execute SQL statements
result = engine.execute_sql("SELECT * FROM users")

# List all tables
tables = engine.list_tables()

# Get table schema
schema = engine.describe_table("users")

# Drop table
result = engine.drop_table("old_table")
```

### JSONDatabase Class

```python
from json_crud import JSONDatabase

db = JSONDatabase("table_name")

# CRUD operations
record_id = db.insert({"name": "John", "age": 30})
records = db.read(filters={"age": lambda x: x > 25})
updated = db.update(record_id, {"age": 31})
deleted = db.delete(record_id)

# Utility methods
count = db.count()
db.clear()  # Remove all records
```

### Convenience Functions

```python
from json_crud import insert_record, read_records, update_record, delete_record

# Quick operations without creating database instances
user_id = insert_record("users", {"name": "Jane"})
users = read_records("users", filters={"active": True})
updated = update_record("users", user_id, {"last_login": "2023-12-07"})
deleted = delete_record("users", user_id)
```

## 📄 File Format

Database files are stored as JSON arrays with automatic metadata:

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

Schema registry (`_schemas.json`):
```json
{
  "users": {
    "table_name": "users",
    "columns": {
      "id": {"type": "INT", "constraints": ["PRIMARY KEY", "AUTO_INCREMENT"]},
      "name": {"type": "VARCHAR", "size": 100, "constraints": ["NOT NULL"]},
      "email": {"type": "VARCHAR", "size": 255, "constraints": ["UNIQUE"]}
    },
    "constraints": {
      "primary_key": "id",
      "unique": ["email"]
    },
    "created_at": "2023-12-07T10:30:00.123456"
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
```bash
git clone <repository-url>
cd vdbms
pip install -r requirements.txt
python -m unittest discover -s . -p "test_*.py"
```

## 📜 License

This project is released into the public domain. Use it however you like!

---

**VDBMS** - Where SQL meets JSON simplicity 🚀 