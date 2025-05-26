#!/usr/bin/env python3
"""
SQL Parser Example Script

This script demonstrates the comprehensive capabilities of the SQL parser
with practical examples and use cases.
"""

from sql_parser import (
    SQLParserInterface, CreateTableStatement, InsertStatement, 
    SelectStatement, UpdateStatement, DeleteStatement,
    BinaryOperation, LogicalOperation, WhereClause
)


def analyze_ast(ast, depth=0):
    """Recursively analyze and display AST structure."""
    indent = "  " * depth
    
    if isinstance(ast, CreateTableStatement):
        print(f"{indent}CREATE TABLE: {ast.table_name}")
        print(f"{indent}Columns:")
        for col in ast.columns:
            constraints = " ".join(col.constraints) if col.constraints else "None"
            print(f"{indent}  - {col.name}: {col.data_type} (constraints: {constraints})")
    
    elif isinstance(ast, SelectStatement):
        print(f"{indent}SELECT from: {ast.table_name}")
        if ast.columns == ['*']:
            print(f"{indent}Columns: ALL (*)")
        else:
            print(f"{indent}Columns: {[str(col) for col in ast.columns]}")
        if ast.where_clause:
            print(f"{indent}WHERE clause:")
            analyze_ast(ast.where_clause.condition, depth + 1)
    
    elif isinstance(ast, InsertStatement):
        print(f"{indent}INSERT INTO: {ast.table_name}")
        if ast.columns:
            print(f"{indent}Specified columns: {ast.columns}")
        print(f"{indent}Number of value rows: {len(ast.values)}")
        for i, row in enumerate(ast.values):
            print(f"{indent}  Row {i+1}: {[str(val) for val in row]}")
    
    elif isinstance(ast, UpdateStatement):
        print(f"{indent}UPDATE table: {ast.table_name}")
        print(f"{indent}Assignments:")
        for col, val in ast.assignments:
            print(f"{indent}  {col} = {val}")
        if ast.where_clause:
            print(f"{indent}WHERE clause:")
            analyze_ast(ast.where_clause.condition, depth + 1)
    
    elif isinstance(ast, DeleteStatement):
        print(f"{indent}DELETE FROM: {ast.table_name}")
        if ast.where_clause:
            print(f"{indent}WHERE clause:")
            analyze_ast(ast.where_clause.condition, depth + 1)
    
    elif isinstance(ast, BinaryOperation):
        print(f"{indent}Binary Operation: {ast.left} {ast.operator} {ast.right}")
    
    elif isinstance(ast, LogicalOperation):
        print(f"{indent}Logical Operation: {ast.operator}")
        print(f"{indent}Left:")
        analyze_ast(ast.left, depth + 1)
        print(f"{indent}Right:")
        analyze_ast(ast.right, depth + 1)


def demonstrate_parser():
    """Comprehensive demonstration of SQL parser capabilities."""
    print("=" * 70)
    print("SQL PARSER COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)
    
    parser = SQLParserInterface()
    
    # Example SQL statements with increasing complexity
    examples = [
        {
            "category": "Schema Definition",
            "statements": [
                "CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL)",
                "CREATE TABLE products (id INT, name VARCHAR(255), price FLOAT, category VARCHAR(50))",
                "CREATE TABLE orders (order_id INT PRIMARY KEY, user_id INT, product_id INT, quantity INT, order_date TIMESTAMP)"
            ]
        },
        {
            "category": "Data Insertion",
            "statements": [
                "INSERT INTO users VALUES (1, 'John Doe')",
                "INSERT INTO users (name) VALUES ('Jane Smith'), ('Bob Wilson')",
                "INSERT INTO products (id, name, price, category) VALUES (101, 'Laptop', 999.99, 'Electronics')"
            ]
        },
        {
            "category": "Data Retrieval",
            "statements": [
                "SELECT * FROM users",
                "SELECT name FROM users WHERE id = 1",
                "SELECT name, price FROM products WHERE price > 500.0 AND category = 'Electronics'",
                "SELECT * FROM orders WHERE (quantity > 1 AND order_date > '2023-01-01') OR user_id = 1"
            ]
        },
        {
            "category": "Data Modification",
            "statements": [
                "UPDATE users SET name = 'John Smith' WHERE id = 1",
                "UPDATE products SET price = 899.99, category = 'Tech' WHERE name = 'Laptop'"
            ]
        },
        {
            "category": "Data Deletion",
            "statements": [
                "DELETE FROM users WHERE id = 999",
                "DELETE FROM orders WHERE quantity = 0 AND order_date < '2022-01-01'"
            ]
        },
        {
            "category": "Pattern Matching",
            "statements": [
                "SELECT * FROM users WHERE name LIKE 'John%'",
                "SELECT * FROM products WHERE category LIKE '%tech%'"
            ]
        }
    ]
    
    for category_info in examples:
        print(f"\n{category_info['category'].upper()}")
        print("-" * len(category_info['category']))
        
        for i, sql in enumerate(category_info['statements'], 1):
            print(f"\n{i}. SQL: {sql}")
            
            ast = parser.parse_sql(sql)
            if ast:
                print(f"   ✓ Parsed successfully")
                print(f"   AST Analysis:")
                analyze_ast(ast, 2)
                print(f"   Reconstructed: {str(ast)}")
            else:
                print(f"   ✗ Failed to parse")


def interactive_parser():
    """Interactive SQL parser for user input."""
    print("\n" + "=" * 70)
    print("INTERACTIVE SQL PARSER")
    print("=" * 70)
    print("Enter SQL statements to parse (type 'quit' to exit):")
    
    parser = SQLParserInterface()
    
    while True:
        try:
            sql = input("\nSQL> ").strip()
            
            if sql.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not sql:
                continue
            
            print(f"\nParsing: {sql}")
            ast = parser.parse_sql(sql)
            
            if ast:
                print("✓ Successfully parsed!")
                print(f"AST Type: {type(ast).__name__}")
                print("Detailed Analysis:")
                analyze_ast(ast, 1)
                print(f"Reconstructed SQL: {str(ast)}")
            else:
                print("✗ Failed to parse SQL statement")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def performance_test():
    """Simple performance test for the parser."""
    print("\n" + "=" * 70)
    print("PERFORMANCE TEST")
    print("=" * 70)
    
    import time
    
    parser = SQLParserInterface()
    
    # Test statements
    test_statements = [
        "SELECT * FROM users",
        "INSERT INTO users VALUES (1, 'Test User')",
        "UPDATE users SET name = 'Updated' WHERE id = 1",
        "DELETE FROM users WHERE id = 1",
        "CREATE TABLE test (id INT PRIMARY KEY, data VARCHAR(100))"
    ]
    
    iterations = 100
    
    print(f"Parsing {len(test_statements)} different statements {iterations} times each...")
    
    start_time = time.time()
    
    for _ in range(iterations):
        for sql in test_statements:
            ast = parser.parse_sql(sql)
            if not ast:
                print(f"Failed to parse: {sql}")
    
    end_time = time.time()
    total_time = end_time - start_time
    total_statements = len(test_statements) * iterations
    
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Total statements parsed: {total_statements}")
    print(f"Average time per statement: {(total_time / total_statements) * 1000:.3f} ms")
    print(f"Statements per second: {total_statements / total_time:.1f}")


def main():
    """Main function to run all demonstrations."""
    print("SQL Parser using PLY - Comprehensive Example")
    print("This script demonstrates the full capabilities of the SQL parser.\n")
    
    # Run the comprehensive demonstration
    demonstrate_parser()
    
    # Run performance test
    performance_test()
    
    # Offer interactive mode
    print("\n" + "=" * 70)
    response = input("Would you like to try the interactive parser? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_parser()
    
    print("\nDemonstration complete!")


if __name__ == "__main__":
    main() 