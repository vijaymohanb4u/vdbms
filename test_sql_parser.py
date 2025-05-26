#!/usr/bin/env python3
"""
Test suite for the SQL Parser

This module contains comprehensive tests for the SQL parser functionality,
including lexer tests, parser tests, and AST validation.
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sql_parser import (
    SQLParserInterface, SQLLexer, SQLParser,
    CreateTableStatement, InsertStatement, SelectStatement, 
    UpdateStatement, DeleteStatement, WhereClause,
    DataType, ColumnDefinition, Literal, Identifier,
    BinaryOperation, LogicalOperation
)


class TestSQLLexer(unittest.TestCase):
    """Test the SQL lexer functionality."""
    
    def setUp(self):
        self.lexer = SQLLexer()
        self.lexer.build()
    
    def tokenize(self, input_text):
        """Helper method to tokenize input and return list of tokens."""
        self.lexer.lexer.input(input_text)
        tokens = []
        while True:
            tok = self.lexer.lexer.token()
            if not tok:
                break
            tokens.append((tok.type, tok.value))
        return tokens
    
    def test_keywords(self):
        """Test that SQL keywords are properly recognized."""
        keywords_test = "CREATE TABLE SELECT INSERT UPDATE DELETE FROM WHERE"
        tokens = self.tokenize(keywords_test)
        expected = [
            ('CREATE', 'CREATE'), ('TABLE', 'TABLE'), ('SELECT', 'SELECT'),
            ('INSERT', 'INSERT'), ('UPDATE', 'UPDATE'), ('DELETE', 'DELETE'),
            ('FROM', 'FROM'), ('WHERE', 'WHERE')
        ]
        self.assertEqual(tokens, expected)
    
    def test_identifiers(self):
        """Test identifier recognition."""
        identifiers_test = "users user_name table123 _private"
        tokens = self.tokenize(identifiers_test)
        expected = [
            ('IDENTIFIER', 'users'), ('IDENTIFIER', 'user_name'),
            ('IDENTIFIER', 'table123'), ('IDENTIFIER', '_private')
        ]
        self.assertEqual(tokens, expected)
    
    def test_numbers(self):
        """Test number recognition."""
        numbers_test = "123 45.67 0 999.0"
        tokens = self.tokenize(numbers_test)
        expected = [
            ('NUMBER', 123), ('FLOAT_NUMBER', 45.67),
            ('NUMBER', 0), ('FLOAT_NUMBER', 999.0)
        ]
        self.assertEqual(tokens, expected)
    
    def test_strings(self):
        """Test string literal recognition."""
        strings_test = "'hello' 'world with spaces' 'don\\'t'"
        tokens = self.tokenize(strings_test)
        expected = [
            ('STRING', 'hello'), ('STRING', 'world with spaces'),
            ('STRING', "don't")
        ]
        self.assertEqual(tokens, expected)
    
    def test_operators(self):
        """Test operator recognition."""
        operators_test = "= != < > <= >= ( ) , ;"
        tokens = self.tokenize(operators_test)
        expected = [
            ('EQUALS', '='), ('NOT_EQUALS', '!='), ('LESS_THAN', '<'),
            ('GREATER_THAN', '>'), ('LESS_EQUAL', '<='), ('GREATER_EQUAL', '>='),
            ('LPAREN', '('), ('RPAREN', ')'), ('COMMA', ','), ('SEMICOLON', ';')
        ]
        self.assertEqual(tokens, expected)


class TestSQLParser(unittest.TestCase):
    """Test the SQL parser functionality."""
    
    def setUp(self):
        self.parser = SQLParserInterface()
    
    def test_create_table_simple(self):
        """Test parsing a simple CREATE TABLE statement."""
        sql = "CREATE TABLE users (id INT, name VARCHAR(100))"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, CreateTableStatement)
        self.assertEqual(ast.table_name, "users")
        self.assertEqual(len(ast.columns), 2)
        
        # Check first column
        self.assertEqual(ast.columns[0].name, "id")
        self.assertEqual(ast.columns[0].data_type.type_name, "INT")
        
        # Check second column
        self.assertEqual(ast.columns[1].name, "name")
        self.assertEqual(ast.columns[1].data_type.type_name, "VARCHAR")
        self.assertEqual(ast.columns[1].data_type.size, 100)
    
    def test_create_table_with_constraints(self):
        """Test CREATE TABLE with constraints."""
        sql = "CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, email VARCHAR(255) UNIQUE)"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, CreateTableStatement)
        self.assertEqual(len(ast.columns), 2)
        
        # Check constraints
        self.assertIn("PRIMARY KEY", ast.columns[0].constraints)
        self.assertIn("AUTO_INCREMENT", ast.columns[0].constraints)
        self.assertIn("UNIQUE", ast.columns[1].constraints)
    
    def test_insert_simple(self):
        """Test parsing a simple INSERT statement."""
        sql = "INSERT INTO users VALUES (1, 'John Doe')"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(ast.table_name, "users")
        self.assertIsNone(ast.columns)
        self.assertEqual(len(ast.values), 1)
        self.assertEqual(len(ast.values[0]), 2)
        
        # Check values
        self.assertEqual(ast.values[0][0].value, 1)
        self.assertEqual(ast.values[0][1].value, "John Doe")
    
    def test_insert_with_columns(self):
        """Test INSERT with specified columns."""
        sql = "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(ast.table_name, "users")
        self.assertEqual(ast.columns, ["name", "email"])
        self.assertEqual(len(ast.values), 1)
        self.assertEqual(len(ast.values[0]), 2)
    
    def test_insert_multiple_values(self):
        """Test INSERT with multiple value rows."""
        sql = "INSERT INTO users (name) VALUES ('John'), ('Jane')"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(len(ast.values), 2)
        self.assertEqual(ast.values[0][0].value, "John")
        self.assertEqual(ast.values[1][0].value, "Jane")
    
    def test_select_all(self):
        """Test SELECT * statement."""
        sql = "SELECT * FROM users"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, SelectStatement)
        self.assertEqual(ast.columns, ["*"])
        self.assertEqual(ast.table_name, "users")
        self.assertIsNone(ast.where_clause)
    
    def test_select_columns(self):
        """Test SELECT with specific columns."""
        sql = "SELECT name, email FROM users"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, SelectStatement)
        self.assertEqual(len(ast.columns), 2)
        self.assertEqual(ast.columns[0].name, "name")
        self.assertEqual(ast.columns[1].name, "email")
        self.assertEqual(ast.table_name, "users")
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        sql = "SELECT * FROM users WHERE age > 18"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, SelectStatement)
        self.assertIsNotNone(ast.where_clause)
        self.assertIsInstance(ast.where_clause.condition, BinaryOperation)
        
        condition = ast.where_clause.condition
        self.assertEqual(condition.left.name, "age")
        self.assertEqual(condition.operator, ">")
        self.assertEqual(condition.right.value, 18)
    
    def test_select_with_complex_where(self):
        """Test SELECT with complex WHERE clause."""
        sql = "SELECT * FROM users WHERE age > 18 AND name = 'John'"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, SelectStatement)
        condition = ast.where_clause.condition
        self.assertIsInstance(condition, LogicalOperation)
        self.assertEqual(condition.operator, "AND")
        
        # Check left side (age > 18)
        left_condition = condition.left
        self.assertIsInstance(left_condition, BinaryOperation)
        self.assertEqual(left_condition.left.name, "age")
        self.assertEqual(left_condition.operator, ">")
        self.assertEqual(left_condition.right.value, 18)
        
        # Check right side (name = 'John')
        right_condition = condition.right
        self.assertIsInstance(right_condition, BinaryOperation)
        self.assertEqual(right_condition.left.name, "name")
        self.assertEqual(right_condition.operator, "=")
        self.assertEqual(right_condition.right.value, "John")
    
    def test_update_simple(self):
        """Test simple UPDATE statement."""
        sql = "UPDATE users SET age = 25"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, UpdateStatement)
        self.assertEqual(ast.table_name, "users")
        self.assertEqual(len(ast.assignments), 1)
        self.assertEqual(ast.assignments[0][0], "age")
        self.assertEqual(ast.assignments[0][1].value, 25)
        self.assertIsNone(ast.where_clause)
    
    def test_update_multiple_columns(self):
        """Test UPDATE with multiple columns."""
        sql = "UPDATE users SET age = 25, name = 'John'"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, UpdateStatement)
        self.assertEqual(len(ast.assignments), 2)
        self.assertEqual(ast.assignments[0][0], "age")
        self.assertEqual(ast.assignments[0][1].value, 25)
        self.assertEqual(ast.assignments[1][0], "name")
        self.assertEqual(ast.assignments[1][1].value, "John")
    
    def test_update_with_where(self):
        """Test UPDATE with WHERE clause."""
        sql = "UPDATE users SET age = 25 WHERE id = 1"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, UpdateStatement)
        self.assertIsNotNone(ast.where_clause)
        condition = ast.where_clause.condition
        self.assertEqual(condition.left.name, "id")
        self.assertEqual(condition.operator, "=")
        self.assertEqual(condition.right.value, 1)
    
    def test_delete_simple(self):
        """Test simple DELETE statement."""
        sql = "DELETE FROM users"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, DeleteStatement)
        self.assertEqual(ast.table_name, "users")
        self.assertIsNone(ast.where_clause)
    
    def test_delete_with_where(self):
        """Test DELETE with WHERE clause."""
        sql = "DELETE FROM users WHERE age < 18"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, DeleteStatement)
        self.assertEqual(ast.table_name, "users")
        self.assertIsNotNone(ast.where_clause)
        
        condition = ast.where_clause.condition
        self.assertEqual(condition.left.name, "age")
        self.assertEqual(condition.operator, "<")
        self.assertEqual(condition.right.value, 18)
    
    def test_null_values(self):
        """Test handling of NULL values."""
        sql = "INSERT INTO users VALUES (1, NULL)"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, InsertStatement)
        self.assertEqual(ast.values[0][0].value, 1)
        self.assertIsNone(ast.values[0][1].value)
    
    def test_like_operator(self):
        """Test LIKE operator in WHERE clause."""
        sql = "SELECT * FROM users WHERE name LIKE 'John%'"
        ast = self.parser.parse_sql(sql)
        
        self.assertIsInstance(ast, SelectStatement)
        condition = ast.where_clause.condition
        self.assertEqual(condition.left.name, "name")
        self.assertEqual(condition.operator, "LIKE")
        self.assertEqual(condition.right.value, "John%")


class TestASTStringRepresentation(unittest.TestCase):
    """Test the string representation of AST nodes."""
    
    def setUp(self):
        self.parser = SQLParserInterface()
    
    def test_create_table_str(self):
        """Test CREATE TABLE string representation."""
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100))"
        ast = self.parser.parse_sql(sql)
        
        str_repr = str(ast)
        self.assertIn("CREATE TABLE users", str_repr)
        self.assertIn("id INT PRIMARY KEY", str_repr)
        self.assertIn("name VARCHAR(100)", str_repr)
    
    def test_insert_str(self):
        """Test INSERT string representation."""
        sql = "INSERT INTO users (name) VALUES ('John')"
        ast = self.parser.parse_sql(sql)
        
        str_repr = str(ast)
        self.assertIn("INSERT INTO users", str_repr)
        self.assertIn("(name)", str_repr)
        self.assertIn("VALUES", str_repr)
        self.assertIn("('John')", str_repr)
    
    def test_select_str(self):
        """Test SELECT string representation."""
        sql = "SELECT name, email FROM users WHERE age > 18"
        ast = self.parser.parse_sql(sql)
        
        str_repr = str(ast)
        self.assertIn("SELECT name, email", str_repr)
        self.assertIn("FROM users", str_repr)
        self.assertIn("WHERE", str_repr)
        self.assertIn("age", str_repr)
        self.assertIn(">", str_repr)
        self.assertIn("18", str_repr)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the parser."""
    
    def setUp(self):
        self.parser = SQLParserInterface()
    
    def test_invalid_sql(self):
        """Test parsing invalid SQL returns None."""
        invalid_sql = "INVALID SQL STATEMENT"
        ast = self.parser.parse_sql(invalid_sql)
        self.assertIsNone(ast)
    
    def test_incomplete_sql(self):
        """Test parsing incomplete SQL."""
        incomplete_sql = "SELECT * FROM"
        ast = self.parser.parse_sql(incomplete_sql)
        self.assertIsNone(ast)
    
    def test_syntax_error(self):
        """Test syntax error handling."""
        syntax_error_sql = "SELECT * FROM users WHERE"
        ast = self.parser.parse_sql(syntax_error_sql)
        self.assertIsNone(ast)


def run_demo():
    """Run a demonstration of the SQL parser."""
    print("=== SQL Parser Demonstration ===\n")
    
    parser = SQLParserInterface()
    
    # Test cases with expected behavior
    test_cases = [
        # CREATE TABLE
        {
            "sql": "CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, email VARCHAR(255) UNIQUE)",
            "description": "CREATE TABLE with various constraints"
        },
        
        # INSERT
        {
            "sql": "INSERT INTO users VALUES (1, 'John Doe', 'john@example.com')",
            "description": "Simple INSERT statement"
        },
        {
            "sql": "INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com'), ('Bob Wilson', 'bob@example.com')",
            "description": "INSERT with multiple rows and specified columns"
        },
        
        # SELECT
        {
            "sql": "SELECT * FROM users",
            "description": "Simple SELECT all"
        },
        {
            "sql": "SELECT name, email FROM users WHERE age > 18 AND email LIKE '%@example.com'",
            "description": "SELECT with complex WHERE clause"
        },
        {
            "sql": "SELECT * FROM users WHERE (age > 20 AND age < 40) OR name = 'Admin'",
            "description": "SELECT with parentheses and OR logic"
        },
        
        # UPDATE
        {
            "sql": "UPDATE users SET age = 31, email = 'newemail@example.com' WHERE name = 'John Doe'",
            "description": "UPDATE with multiple columns and WHERE clause"
        },
        
        # DELETE
        {
            "sql": "DELETE FROM users WHERE age < 18",
            "description": "DELETE with WHERE clause"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['description']}")
        print(f"   SQL: {test_case['sql']}")
        
        ast = parser.parse_sql(test_case['sql'])
        if ast:
            print(f"   AST Type: {type(ast).__name__}")
            print(f"   Reconstructed: {str(ast)}")
            print("   ✓ Parsed successfully")
        else:
            print("   ✗ Failed to parse")
        
        print()


if __name__ == "__main__":
    # Run the demonstration first
    run_demo()
    
    # Then run the unit tests
    print("\n" + "="*60)
    print("Running Unit Tests")
    print("="*60)
    unittest.main(verbosity=2) 