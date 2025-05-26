#!/usr/bin/env python3
"""
SQL-to-JSON Database Engine

This module integrates the SQL parser with the JSON CRUD system to provide
a complete SQL interface for JSON-based database operations.
"""

import os
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from sql_parser import (
    SQLParserInterface, CreateTableStatement, InsertStatement,
    SelectStatement, UpdateStatement, DeleteStatement,
    BinaryOperation, LogicalOperation, WhereClause,
    Literal, Identifier
)
from json_crud import JSONDatabase, create_database, list_databases
from config import config


class SQLExecutionError(Exception):
    """Exception raised during SQL execution."""
    pass


class SQLToJSONEngine:
    """SQL execution engine that operates on JSON files."""
    
    def __init__(self):
        self.parser = SQLParserInterface()
        self.schema_registry = {}  # Store table schemas
        self._load_existing_schemas()
    
    def _load_existing_schemas(self):
        """Load schemas for existing JSON database files."""
        try:
            schema_file = config.get_db_path("_schemas.json")
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    self.schema_registry = json.load(f)
        except Exception:
            self.schema_registry = {}
    
    def _save_schemas(self):
        """Save table schemas to a registry file."""
        try:
            schema_file = config.get_db_path("_schemas.json")
            with open(schema_file, 'w') as f:
                json.dump(self.schema_registry, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save schema registry: {e}")
    
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL statement and return results.
        
        Args:
            sql (str): SQL statement to execute
            
        Returns:
            Dict[str, Any]: Execution results with status, data, and metadata
        """
        try:
            # Parse the SQL statement
            ast = self.parser.parse_sql(sql)
            if not ast:
                return {
                    "success": False,
                    "error": "Failed to parse SQL statement",
                    "sql": sql
                }
            
            # Execute based on statement type
            if isinstance(ast, CreateTableStatement):
                return self._execute_create_table(ast)
            elif isinstance(ast, InsertStatement):
                return self._execute_insert(ast)
            elif isinstance(ast, SelectStatement):
                return self._execute_select(ast)
            elif isinstance(ast, UpdateStatement):
                return self._execute_update(ast)
            elif isinstance(ast, DeleteStatement):
                return self._execute_delete(ast)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported statement type: {type(ast).__name__}",
                    "sql": sql
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sql": sql
            }
    
    def _execute_create_table(self, ast: CreateTableStatement) -> Dict[str, Any]:
        """Execute CREATE TABLE statement."""
        table_name = ast.table_name
        
        # Check if table already exists
        db_file = f"{table_name}.json"
        if os.path.exists(config.get_db_path(db_file)):
            return {
                "success": False,
                "error": f"Table '{table_name}' already exists",
                "table": table_name
            }
        
        # Create the table schema
        schema = {
            "table_name": table_name,
            "columns": {},
            "constraints": {},
            "created_at": datetime.now().isoformat()
        }
        
        for col in ast.columns:
            schema["columns"][col.name] = {
                "type": col.data_type.type_name,
                "size": col.data_type.size,
                "constraints": col.constraints
            }
            
            # Handle constraints
            if "PRIMARY KEY" in col.constraints:
                schema["constraints"]["primary_key"] = col.name
            if "UNIQUE" in col.constraints:
                if "unique" not in schema["constraints"]:
                    schema["constraints"]["unique"] = []
                schema["constraints"]["unique"].append(col.name)
        
        # Store schema
        self.schema_registry[table_name] = schema
        self._save_schemas()
        
        # Create empty JSON database file
        db = create_database(db_file)
        
        return {
            "success": True,
            "message": f"Table '{table_name}' created successfully",
            "table": table_name,
            "schema": schema
        }
    
    def _execute_insert(self, ast: InsertStatement) -> Dict[str, Any]:
        """Execute INSERT statement."""
        table_name = ast.table_name
        
        # Check if table exists
        if table_name not in self.schema_registry:
            return {
                "success": False,
                "error": f"Table '{table_name}' does not exist",
                "table": table_name
            }
        
        schema = self.schema_registry[table_name]
        db = JSONDatabase(f"{table_name}.json")
        
        inserted_records = []
        
        for value_row in ast.values:
            # Build record from values
            record = {}
            
            if ast.columns:
                # Use specified columns
                if len(value_row) != len(ast.columns):
                    return {
                        "success": False,
                        "error": f"Column count mismatch: expected {len(ast.columns)}, got {len(value_row)}",
                        "table": table_name
                    }
                
                for i, col_name in enumerate(ast.columns):
                    value = self._convert_literal_value(value_row[i])
                    record[col_name] = value
            else:
                # Use all columns in schema order
                column_names = list(schema["columns"].keys())
                if len(value_row) != len(column_names):
                    return {
                        "success": False,
                        "error": f"Column count mismatch: expected {len(column_names)}, got {len(value_row)}",
                        "table": table_name
                    }
                
                for i, col_name in enumerate(column_names):
                    value = self._convert_literal_value(value_row[i])
                    record[col_name] = value
            
            # Validate constraints
            validation_result = self._validate_record(record, schema, db)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "table": table_name
                }
            
            # Insert record
            try:
                record_id = db.insert(record, auto_id=True)
                inserted_records.append({"id": record_id, "record": record})
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to insert record: {e}",
                    "table": table_name
                }
        
        return {
            "success": True,
            "message": f"Inserted {len(inserted_records)} record(s) into '{table_name}'",
            "table": table_name,
            "inserted_count": len(inserted_records),
            "records": inserted_records
        }
    
    def _execute_select(self, ast: SelectStatement) -> Dict[str, Any]:
        """Execute SELECT statement."""
        table_name = ast.table_name
        
        # Check if table exists
        if table_name not in self.schema_registry:
            return {
                "success": False,
                "error": f"Table '{table_name}' does not exist",
                "table": table_name
            }
        
        db = JSONDatabase(f"{table_name}.json")
        
        try:
            # Get all records first
            all_records = db.read()
            
            # Apply WHERE clause if present
            if ast.where_clause:
                filtered_records = []
                for record in all_records:
                    if self._evaluate_condition(ast.where_clause.condition, record):
                        filtered_records.append(record)
                records = filtered_records
            else:
                records = all_records
            
            # Apply column selection
            if ast.columns == ['*']:
                # Select all columns
                result_records = records
            else:
                # Select specific columns
                column_names = [col.name if hasattr(col, 'name') else str(col) for col in ast.columns]
                result_records = []
                for record in records:
                    selected_record = {}
                    for col_name in column_names:
                        if col_name in record:
                            selected_record[col_name] = record[col_name]
                        else:
                            selected_record[col_name] = None
                    result_records.append(selected_record)
            
            return {
                "success": True,
                "table": table_name,
                "records": result_records,
                "count": len(result_records),
                "columns": ast.columns if ast.columns != ['*'] else list(self.schema_registry[table_name]["columns"].keys())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute SELECT: {e}",
                "table": table_name
            }
    
    def _execute_update(self, ast: UpdateStatement) -> Dict[str, Any]:
        """Execute UPDATE statement."""
        table_name = ast.table_name
        
        # Check if table exists
        if table_name not in self.schema_registry:
            return {
                "success": False,
                "error": f"Table '{table_name}' does not exist",
                "table": table_name
            }
        
        schema = self.schema_registry[table_name]
        db = JSONDatabase(f"{table_name}.json")
        
        try:
            # Get all records
            all_records = db.read()
            updated_count = 0
            
            for record in all_records:
                # Check if record matches WHERE clause
                should_update = True
                if ast.where_clause:
                    should_update = self._evaluate_condition(ast.where_clause.condition, record)
                
                if should_update:
                    # Apply updates
                    updates = {}
                    for col_name, value_literal in ast.assignments:
                        value = self._convert_literal_value(value_literal)
                        updates[col_name] = value
                    
                    # Validate updated record
                    updated_record = {**record, **updates}
                    validation_result = self._validate_record(updated_record, schema, db, exclude_id=record.get('id'))
                    if not validation_result["valid"]:
                        return {
                            "success": False,
                            "error": validation_result["error"],
                            "table": table_name
                        }
                    
                    # Update the record
                    db.update(record['id'], updates)
                    updated_count += 1
            
            return {
                "success": True,
                "message": f"Updated {updated_count} record(s) in '{table_name}'",
                "table": table_name,
                "updated_count": updated_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute UPDATE: {e}",
                "table": table_name
            }
    
    def _execute_delete(self, ast: DeleteStatement) -> Dict[str, Any]:
        """Execute DELETE statement."""
        table_name = ast.table_name
        
        # Check if table exists
        if table_name not in self.schema_registry:
            return {
                "success": False,
                "error": f"Table '{table_name}' does not exist",
                "table": table_name
            }
        
        db = JSONDatabase(f"{table_name}.json")
        
        try:
            # Get all records
            all_records = db.read()
            deleted_count = 0
            
            # Collect IDs of records to delete
            records_to_delete = []
            for record in all_records:
                should_delete = True
                if ast.where_clause:
                    should_delete = self._evaluate_condition(ast.where_clause.condition, record)
                
                if should_delete:
                    records_to_delete.append(record['id'])
            
            # Delete records
            for record_id in records_to_delete:
                if db.delete(record_id):
                    deleted_count += 1
            
            return {
                "success": True,
                "message": f"Deleted {deleted_count} record(s) from '{table_name}'",
                "table": table_name,
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute DELETE: {e}",
                "table": table_name
            }
    
    def _evaluate_condition(self, condition, record: Dict[str, Any]) -> bool:
        """Evaluate a WHERE condition against a record."""
        if isinstance(condition, BinaryOperation):
            left_value = self._get_field_value(condition.left, record)
            right_value = self._convert_literal_value(condition.right)
            
            operator = condition.operator
            
            if operator == '=':
                return left_value == right_value
            elif operator in ['!=', '<>']:
                return left_value != right_value
            elif operator == '<':
                return left_value < right_value
            elif operator == '>':
                return left_value > right_value
            elif operator == '<=':
                return left_value <= right_value
            elif operator == '>=':
                return left_value >= right_value
            elif operator == 'LIKE':
                if isinstance(left_value, str) and isinstance(right_value, str):
                    # Simple LIKE implementation (% as wildcard)
                    pattern = right_value.replace('%', '.*')
                    import re
                    return bool(re.match(pattern, left_value))
                return False
            else:
                raise SQLExecutionError(f"Unsupported operator: {operator}")
        
        elif isinstance(condition, LogicalOperation):
            left_result = self._evaluate_condition(condition.left, record)
            right_result = self._evaluate_condition(condition.right, record)
            
            if condition.operator == 'AND':
                return left_result and right_result
            elif condition.operator == 'OR':
                return left_result or right_result
            else:
                raise SQLExecutionError(f"Unsupported logical operator: {condition.operator}")
        
        else:
            raise SQLExecutionError(f"Unsupported condition type: {type(condition)}")
    
    def _get_field_value(self, field, record: Dict[str, Any]):
        """Get field value from record."""
        if isinstance(field, Identifier):
            return record.get(field.name)
        elif isinstance(field, Literal):
            return field.value
        else:
            raise SQLExecutionError(f"Unsupported field type: {type(field)}")
    
    def _convert_literal_value(self, literal):
        """Convert a Literal AST node to its Python value."""
        if isinstance(literal, Literal):
            return literal.value
        else:
            return literal
    
    def _validate_record(self, record: Dict[str, Any], schema: Dict[str, Any], 
                        db: JSONDatabase, exclude_id: str = None) -> Dict[str, Any]:
        """Validate a record against table schema and constraints."""
        # Check required columns (NOT NULL)
        for col_name, col_info in schema["columns"].items():
            if "NOT NULL" in col_info.get("constraints", []):
                if col_name not in record or record[col_name] is None:
                    return {
                        "valid": False,
                        "error": f"Column '{col_name}' cannot be NULL"
                    }
        
        # Check unique constraints
        if "unique" in schema.get("constraints", {}):
            for unique_col in schema["constraints"]["unique"]:
                if unique_col in record and record[unique_col] is not None:
                    # Check if value already exists
                    existing_records = db.read(filters={unique_col: record[unique_col]})
                    # Exclude current record if updating
                    if exclude_id:
                        existing_records = [r for r in existing_records if r.get('id') != exclude_id]
                    
                    if existing_records:
                        return {
                            "valid": False,
                            "error": f"Duplicate value for unique column '{unique_col}': {record[unique_col]}"
                        }
        
        # Check primary key constraint
        if "primary_key" in schema.get("constraints", {}):
            pk_col = schema["constraints"]["primary_key"]
            if pk_col in record and record[pk_col] is not None:
                # Check if primary key already exists
                existing_records = db.read(filters={pk_col: record[pk_col]})
                # Exclude current record if updating
                if exclude_id:
                    existing_records = [r for r in existing_records if r.get('id') != exclude_id]
                
                if existing_records:
                    return {
                        "valid": False,
                        "error": f"Duplicate value for primary key '{pk_col}': {record[pk_col]}"
                    }
        
        return {"valid": True}
    
    def list_tables(self) -> List[str]:
        """List all available tables."""
        return list(self.schema_registry.keys())
    
    def describe_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get table schema information."""
        return self.schema_registry.get(table_name)
    
    def drop_table(self, table_name: str) -> Dict[str, Any]:
        """Drop a table (delete JSON file and remove from schema)."""
        if table_name not in self.schema_registry:
            return {
                "success": False,
                "error": f"Table '{table_name}' does not exist"
            }
        
        try:
            # Remove JSON file
            db_file = config.get_db_path(f"{table_name}.json")
            if os.path.exists(db_file):
                os.remove(db_file)
            
            # Remove from schema registry
            del self.schema_registry[table_name]
            self._save_schemas()
            
            return {
                "success": True,
                "message": f"Table '{table_name}' dropped successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to drop table: {e}"
            }


class SQLConsole:
    """Interactive SQL console for the JSON database engine."""
    
    def __init__(self):
        self.engine = SQLToJSONEngine()
    
    def run(self):
        """Run the interactive SQL console."""
        print("=" * 60)
        print("SQL-to-JSON Database Console")
        print("=" * 60)
        print("Enter SQL statements to execute on JSON files.")
        print("Type 'help' for commands, 'quit' to exit.")
        print()
        
        while True:
            try:
                sql = input("SQL> ").strip()
                
                if sql.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if sql.lower() == 'help':
                    self._show_help()
                    continue
                
                if sql.lower() == 'show tables':
                    self._show_tables()
                    continue
                
                if sql.lower().startswith('describe '):
                    table_name = sql[9:].strip()
                    self._describe_table(table_name)
                    continue
                
                if not sql:
                    continue
                
                # Execute SQL
                result = self.engine.execute_sql(sql)
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self):
        """Show help information."""
        print("\nAvailable commands:")
        print("  SHOW TABLES           - List all tables")
        print("  DESCRIBE <table>      - Show table schema")
        print("  CREATE TABLE ...      - Create a new table")
        print("  INSERT INTO ...       - Insert data")
        print("  SELECT ...            - Query data")
        print("  UPDATE ...            - Update data")
        print("  DELETE FROM ...       - Delete data")
        print("  HELP                  - Show this help")
        print("  QUIT                  - Exit console")
        print()
    
    def _show_tables(self):
        """Show all tables."""
        tables = self.engine.list_tables()
        if tables:
            print(f"\nTables ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
        else:
            print("\nNo tables found.")
        print()
    
    def _describe_table(self, table_name: str):
        """Describe a table schema."""
        schema = self.engine.describe_table(table_name)
        if schema:
            print(f"\nTable: {table_name}")
            print("Columns:")
            for col_name, col_info in schema["columns"].items():
                constraints = ", ".join(col_info.get("constraints", []))
                size_info = f"({col_info['size']})" if col_info.get('size') else ""
                constraint_info = f" [{constraints}]" if constraints else ""
                print(f"  - {col_name}: {col_info['type']}{size_info}{constraint_info}")
            
            if "constraints" in schema:
                print("Table constraints:")
                for constraint_type, constraint_value in schema["constraints"].items():
                    print(f"  - {constraint_type}: {constraint_value}")
            
            print(f"Created: {schema.get('created_at', 'Unknown')}")
        else:
            print(f"\nTable '{table_name}' not found.")
        print()
    
    def _display_result(self, result: Dict[str, Any]):
        """Display execution result."""
        if result["success"]:
            if "records" in result:
                # SELECT result
                records = result["records"]
                if records:
                    print(f"\nQuery result ({result['count']} rows):")
                    
                    # Get column names
                    if records:
                        columns = list(records[0].keys())
                        
                        # Print header
                        header = " | ".join(f"{col:15}" for col in columns)
                        print(header)
                        print("-" * len(header))
                        
                        # Print rows
                        for record in records:
                            row = " | ".join(f"{str(record.get(col, 'NULL')):15}" for col in columns)
                            print(row)
                else:
                    print("\nNo records found.")
            else:
                # Other operations
                print(f"\n✓ {result.get('message', 'Operation completed successfully')}")
                
                if "inserted_count" in result:
                    print(f"  Inserted: {result['inserted_count']} records")
                elif "updated_count" in result:
                    print(f"  Updated: {result['updated_count']} records")
                elif "deleted_count" in result:
                    print(f"  Deleted: {result['deleted_count']} records")
        else:
            print(f"\n✗ Error: {result['error']}")
        
        print()


def main():
    """Main function to run the SQL console."""
    console = SQLConsole()
    console.run()


if __name__ == "__main__":
    main() 