#!/usr/bin/env python3
"""
SQL Parser using PLY (Python Lex-Yacc)

This module provides a complete SQL parser that supports:
- CREATE TABLE statements
- INSERT INTO statements  
- SELECT statements with WHERE clauses
- UPDATE statements with WHERE clauses
- DELETE FROM statements with WHERE clauses

The parser generates an Abstract Syntax Tree (AST) for parsed SQL statements.
"""

import ply.lex as lex
import ply.yacc as yacc
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


# =============================================================================
# AST Node Definitions
# =============================================================================

@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes."""
    pass


@dataclass
class DataType(ASTNode):
    """Represents a SQL data type."""
    type_name: str
    size: Optional[int] = None
    
    def __str__(self):
        if self.size:
            return f"{self.type_name}({self.size})"
        return self.type_name


@dataclass
class ColumnDefinition(ASTNode):
    """Represents a column definition in CREATE TABLE."""
    name: str
    data_type: DataType
    constraints: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
    
    def __str__(self):
        constraints_str = " ".join(self.constraints)
        return f"{self.name} {self.data_type} {constraints_str}".strip()


@dataclass
class CreateTableStatement(ASTNode):
    """Represents a CREATE TABLE statement."""
    table_name: str
    columns: List[ColumnDefinition]
    
    def __str__(self):
        columns_str = ",\n  ".join(str(col) for col in self.columns)
        return f"CREATE TABLE {self.table_name} (\n  {columns_str}\n)"


@dataclass
class Literal(ASTNode):
    """Represents a literal value."""
    value: Union[str, int, float, bool, None]
    
    def __str__(self):
        if isinstance(self.value, str):
            return f"'{self.value}'"
        elif self.value is None:
            return "NULL"
        return str(self.value)


@dataclass
class Identifier(ASTNode):
    """Represents an identifier (table name, column name, etc.)."""
    name: str
    
    def __str__(self):
        return self.name


@dataclass
class BinaryOperation(ASTNode):
    """Represents a binary operation (=, <, >, etc.)."""
    left: ASTNode
    operator: str
    right: ASTNode
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


@dataclass
class LogicalOperation(ASTNode):
    """Represents a logical operation (AND, OR)."""
    left: ASTNode
    operator: str
    right: ASTNode
    
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


@dataclass
class WhereClause(ASTNode):
    """Represents a WHERE clause."""
    condition: ASTNode
    
    def __str__(self):
        return f"WHERE {self.condition}"


@dataclass
class InsertStatement(ASTNode):
    """Represents an INSERT INTO statement."""
    table_name: str
    columns: Optional[List[str]] = None
    values: List[List[ASTNode]] = None
    
    def __post_init__(self):
        if self.values is None:
            self.values = []
    
    def __str__(self):
        if self.columns:
            columns_str = f"({', '.join(self.columns)})"
        else:
            columns_str = ""
        
        values_list = []
        for value_row in self.values:
            values_str = ", ".join(str(v) for v in value_row)
            values_list.append(f"({values_str})")
        
        all_values = ", ".join(values_list)
        return f"INSERT INTO {self.table_name} {columns_str} VALUES {all_values}"


@dataclass
class SelectStatement(ASTNode):
    """Represents a SELECT statement."""
    columns: List[Union[str, Identifier]]
    table_name: str
    where_clause: Optional[WhereClause] = None
    
    def __str__(self):
        if self.columns == ['*']:
            columns_str = "*"
        else:
            columns_str = ", ".join(str(col) for col in self.columns)
        
        query = f"SELECT {columns_str} FROM {self.table_name}"
        if self.where_clause:
            query += f" {self.where_clause}"
        return query


@dataclass
class UpdateStatement(ASTNode):
    """Represents an UPDATE statement."""
    table_name: str
    assignments: List[tuple]  # List of (column, value) tuples
    where_clause: Optional[WhereClause] = None
    
    def __str__(self):
        assignments_str = ", ".join(f"{col} = {val}" for col, val in self.assignments)
        query = f"UPDATE {self.table_name} SET {assignments_str}"
        if self.where_clause:
            query += f" {self.where_clause}"
        return query


@dataclass
class DeleteStatement(ASTNode):
    """Represents a DELETE FROM statement."""
    table_name: str
    where_clause: Optional[WhereClause] = None
    
    def __str__(self):
        query = f"DELETE FROM {self.table_name}"
        if self.where_clause:
            query += f" {self.where_clause}"
        return query


# =============================================================================
# Lexer Definition
# =============================================================================

class SQLLexer:
    """SQL Lexer using PLY."""
    
    # Reserved words
    reserved = {
        'CREATE': 'CREATE',
        'TABLE': 'TABLE',
        'INSERT': 'INSERT',
        'INTO': 'INTO',
        'VALUES': 'VALUES',
        'SELECT': 'SELECT',
        'FROM': 'FROM',
        'WHERE': 'WHERE',
        'UPDATE': 'UPDATE',
        'SET': 'SET',
        'DELETE': 'DELETE',
        'AND': 'AND',
        'OR': 'OR',
        'NOT': 'NOT',
        'NULL': 'NULL',
        'LIKE': 'LIKE',
        'PRIMARY': 'PRIMARY',
        'KEY': 'KEY',
        'UNIQUE': 'UNIQUE',
        'AUTO_INCREMENT': 'AUTO_INCREMENT',
        'VARCHAR': 'VARCHAR',
        'INT': 'INT',
        'INTEGER': 'INTEGER',
        'FLOAT': 'FLOAT',
        'DOUBLE': 'DOUBLE',
        'TEXT': 'TEXT',
        'BOOLEAN': 'BOOLEAN',
        'DATE': 'DATE',
        'DATETIME': 'DATETIME',
        'TIMESTAMP': 'TIMESTAMP',
    }
    
    # Token list
    tokens = [
        'IDENTIFIER',
        'STRING',
        'NUMBER',
        'FLOAT_NUMBER',
        'LPAREN',
        'RPAREN',
        'COMMA',
        'SEMICOLON',
        'EQUALS',
        'NOT_EQUALS',
        'LESS_THAN',
        'GREATER_THAN',
        'LESS_EQUAL',
        'GREATER_EQUAL',
        'LIKE',
        'ASTERISK',
    ] + list(reserved.values())
    
    # Token rules
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_EQUALS = r'='
    t_NOT_EQUALS = r'(!= | <>)'
    t_LESS_THAN = r'<'
    t_GREATER_THAN = r'>'
    t_LESS_EQUAL = r'<='
    t_GREATER_EQUAL = r'>='
    t_ASTERISK = r'\*'
    
    # Ignored characters (spaces and tabs)
    t_ignore = ' \t'
    
    def t_FLOAT_NUMBER(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t
    
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
    
    def t_STRING(self, t):
        r"'([^'\\]|\\.)*'"
        # Remove quotes and handle escape sequences
        t.value = t.value[1:-1].replace("\\'", "'").replace("\\\\", "\\")
        return t
    
    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # Check for reserved words
        t.type = self.reserved.get(t.value.upper(), 'IDENTIFIER')
        return t
    
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)
    
    def build(self, **kwargs):
        """Build the lexer."""
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer


# =============================================================================
# Parser Definition
# =============================================================================

class SQLParser:
    """SQL Parser using PLY."""
    
    def __init__(self):
        self.lexer = SQLLexer()
        self.tokens = self.lexer.tokens
        self.parser = None
        self.build()
    
    def build(self, **kwargs):
        """Build the parser."""
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs)
    
    def parse(self, input_text):
        """Parse SQL input and return AST."""
        try:
            result = self.parser.parse(input_text, lexer=self.lexer.lexer)
            return result
        except Exception as e:
            print(f"Parse error: {e}")
            return None
    
    # =============================================================================
    # Grammar Rules
    # =============================================================================
    
    # Precedence and associativity
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQUALS', 'NOT_EQUALS', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL', 'LIKE'),
        ('right', 'NOT'),
    )
    
    def p_statement(self, p):
        '''statement : create_table_statement
                    | insert_statement
                    | select_statement
                    | update_statement
                    | delete_statement'''
        p[0] = p[1]
    
    # CREATE TABLE statement
    def p_create_table_statement(self, p):
        '''create_table_statement : CREATE TABLE IDENTIFIER LPAREN column_definitions RPAREN'''
        p[0] = CreateTableStatement(table_name=p[3], columns=p[5])
    
    def p_column_definitions(self, p):
        '''column_definitions : column_definition
                             | column_definitions COMMA column_definition'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_column_definition(self, p):
        '''column_definition : IDENTIFIER data_type
                            | IDENTIFIER data_type column_constraints'''
        if len(p) == 3:
            p[0] = ColumnDefinition(name=p[1], data_type=p[2])
        else:
            p[0] = ColumnDefinition(name=p[1], data_type=p[2], constraints=p[3])
    
    def p_data_type(self, p):
        '''data_type : VARCHAR LPAREN NUMBER RPAREN
                    | INT
                    | INTEGER
                    | FLOAT
                    | DOUBLE
                    | TEXT
                    | BOOLEAN
                    | DATE
                    | DATETIME
                    | TIMESTAMP'''
        if len(p) == 2:
            p[0] = DataType(type_name=p[1])
        else:
            p[0] = DataType(type_name=p[1], size=p[3])
    
    def p_column_constraints(self, p):
        '''column_constraints : column_constraint
                             | column_constraints column_constraint'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
    
    def p_column_constraint(self, p):
        '''column_constraint : PRIMARY KEY
                            | UNIQUE
                            | AUTO_INCREMENT
                            | NOT NULL'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = f"{p[1]} {p[2]}"
    
    # INSERT statement
    def p_insert_statement(self, p):
        '''insert_statement : INSERT INTO IDENTIFIER VALUES value_lists
                           | INSERT INTO IDENTIFIER LPAREN column_list RPAREN VALUES value_lists'''
        if len(p) == 6:
            p[0] = InsertStatement(table_name=p[3], values=p[5])
        else:
            p[0] = InsertStatement(table_name=p[3], columns=p[5], values=p[8])
    
    def p_column_list(self, p):
        '''column_list : IDENTIFIER
                      | column_list COMMA IDENTIFIER'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_value_lists(self, p):
        '''value_lists : value_list
                      | value_lists COMMA value_list'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_value_list(self, p):
        '''value_list : LPAREN values RPAREN'''
        p[0] = p[2]
    
    def p_values(self, p):
        '''values : value
                 | values COMMA value'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_value(self, p):
        '''value : STRING
                | NUMBER
                | FLOAT_NUMBER
                | NULL'''
        if p[1] == 'NULL':
            p[0] = Literal(value=None)
        else:
            p[0] = Literal(value=p[1])
    
    # SELECT statement
    def p_select_statement(self, p):
        '''select_statement : SELECT select_list FROM IDENTIFIER
                           | SELECT select_list FROM IDENTIFIER where_clause'''
        if len(p) == 5:
            p[0] = SelectStatement(columns=p[2], table_name=p[4])
        else:
            p[0] = SelectStatement(columns=p[2], table_name=p[4], where_clause=p[5])
    
    def p_select_list(self, p):
        '''select_list : ASTERISK
                      | column_list'''
        if p[1] == '*':
            p[0] = ['*']
        else:
            p[0] = [Identifier(name=col) for col in p[1]]
    
    # UPDATE statement
    def p_update_statement(self, p):
        '''update_statement : UPDATE IDENTIFIER SET assignment_list
                           | UPDATE IDENTIFIER SET assignment_list where_clause'''
        if len(p) == 5:
            p[0] = UpdateStatement(table_name=p[2], assignments=p[4])
        else:
            p[0] = UpdateStatement(table_name=p[2], assignments=p[4], where_clause=p[5])
    
    def p_assignment_list(self, p):
        '''assignment_list : assignment
                          | assignment_list COMMA assignment'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    def p_assignment(self, p):
        '''assignment : IDENTIFIER EQUALS value'''
        p[0] = (p[1], p[3])
    
    # DELETE statement
    def p_delete_statement(self, p):
        '''delete_statement : DELETE FROM IDENTIFIER
                           | DELETE FROM IDENTIFIER where_clause'''
        if len(p) == 4:
            p[0] = DeleteStatement(table_name=p[3])
        else:
            p[0] = DeleteStatement(table_name=p[3], where_clause=p[4])
    
    # WHERE clause
    def p_where_clause(self, p):
        '''where_clause : WHERE condition'''
        p[0] = WhereClause(condition=p[2])
    
    def p_condition(self, p):
        '''condition : condition AND condition
                    | condition OR condition
                    | comparison
                    | LPAREN condition RPAREN'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4 and p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = LogicalOperation(left=p[1], operator=p[2], right=p[3])
    
    def p_comparison(self, p):
        '''comparison : IDENTIFIER EQUALS value
                     | IDENTIFIER NOT_EQUALS value
                     | IDENTIFIER LESS_THAN value
                     | IDENTIFIER GREATER_THAN value
                     | IDENTIFIER LESS_EQUAL value
                     | IDENTIFIER GREATER_EQUAL value
                     | IDENTIFIER LIKE value'''
        left = Identifier(name=p[1])
        right = p[3] if isinstance(p[3], Literal) else Literal(value=p[3])
        p[0] = BinaryOperation(left=left, operator=p[2], right=right)
    
    # Error handling
    def p_error(self, p):
        if p:
            print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
        else:
            print("Syntax error at EOF")


# =============================================================================
# SQL Parser Interface
# =============================================================================

class SQLParserInterface:
    """High-level interface for the SQL parser."""
    
    def __init__(self):
        self.parser = SQLParser()
    
    def parse_sql(self, sql_text: str) -> Optional[ASTNode]:
        """
        Parse SQL text and return AST.
        
        Args:
            sql_text (str): SQL statement to parse
            
        Returns:
            Optional[ASTNode]: Parsed AST or None if parsing failed
        """
        # Clean up the input
        sql_text = sql_text.strip()
        if sql_text.endswith(';'):
            sql_text = sql_text[:-1]
        
        return self.parser.parse(sql_text)
    
    def parse_and_print(self, sql_text: str) -> None:
        """
        Parse SQL and print the resulting AST.
        
        Args:
            sql_text (str): SQL statement to parse
        """
        print(f"Parsing: {sql_text}")
        ast = self.parse_sql(sql_text)
        if ast:
            print(f"AST: {ast}")
            print(f"Reconstructed SQL: {str(ast)}")
        else:
            print("Failed to parse SQL")
        print("-" * 50)


# =============================================================================
# Example Usage and Testing
# =============================================================================

def main():
    """Demonstrate the SQL parser with various examples."""
    parser = SQLParserInterface()
    
    # Test SQL statements
    test_statements = [
        # CREATE TABLE
        """CREATE TABLE users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE,
            age INT,
            created_at TIMESTAMP
        )""",
        
        # INSERT statements
        "INSERT INTO users VALUES (1, 'John Doe', 'john@example.com', 30, NULL)",
        "INSERT INTO users (name, email, age) VALUES ('Jane Smith', 'jane@example.com', 25)",
        "INSERT INTO users (name, email) VALUES ('Bob Wilson', 'bob@example.com'), ('Alice Brown', 'alice@example.com')",
        
        # SELECT statements
        "SELECT * FROM users",
        "SELECT name, email FROM users",
        "SELECT * FROM users WHERE age > 25",
        "SELECT name FROM users WHERE age >= 18 AND email LIKE '%@example.com'",
        "SELECT * FROM users WHERE (age > 20 AND age < 40) OR name = 'Admin'",
        
        # UPDATE statements
        "UPDATE users SET age = 31 WHERE name = 'John Doe'",
        "UPDATE users SET email = 'newemail@example.com', age = 26 WHERE id = 2",
        
        # DELETE statements
        "DELETE FROM users WHERE age < 18",
        "DELETE FROM users WHERE name = 'John Doe' AND age > 30",
    ]
    
    print("=== SQL Parser Demo ===\n")
    
    for sql in test_statements:
        parser.parse_and_print(sql)


if __name__ == "__main__":
    main() 