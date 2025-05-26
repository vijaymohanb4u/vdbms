import json
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
from config import config


class JSONDatabase:
    """A simple JSON-based database for CRUD operations."""
    
    def __init__(self, file_path: str):
        """
        Initialize the JSON database.
        
        Args:
            file_path (str): Database filename (will be placed in configured db directory)
        """
        # Use config to get the full path in the db directory
        self.file_path = config.get_db_path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the JSON file exists, create it if it doesn't."""
        try:
            # Ensure the database directory exists
            config.ensure_db_directory()
            
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w') as f:
                    json.dump([], f)
        except Exception as e:
            raise IOError(f"Failed to create JSON file: {e}")
    
    def _read_data(self) -> List[Dict[str, Any]]:
        """
        Read data from the JSON file.
        
        Returns:
            List[Dict[str, Any]]: List of records
            
        Raises:
            IOError: If file cannot be read
            json.JSONDecodeError: If JSON is invalid
        """
        try:
            with open(self.file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            raise IOError(f"File not found: {self.file_path}")
        except json.JSONDecodeError as e:
            # If the file is empty or contains invalid JSON, return empty list
            # This handles the case where the file exists but is empty
            return []
        except Exception as e:
            raise IOError(f"Error reading file {self.file_path}: {e}")
    
    def _write_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Write data to the JSON file.
        
        Args:
            data (List[Dict[str, Any]]): Data to write
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            with open(self.file_path, 'w') as f:
                if config.pretty_print:
                    json.dump(data, f, indent=2, default=str)
                else:
                    json.dump(data, f, default=str)
        except Exception as e:
            raise IOError(f"Error writing to file {self.file_path}: {e}")
    
    def insert(self, record: Dict[str, Any], auto_id: bool = True) -> str:
        """
        Insert a new record into the JSON database.
        
        Args:
            record (Dict[str, Any]): Record to insert
            auto_id (bool): Whether to automatically generate an ID
            
        Returns:
            str: ID of the inserted record
            
        Raises:
            ValueError: If record is invalid
            IOError: If file operations fail
        """
        if not isinstance(record, dict):
            raise ValueError("Record must be a dictionary")
        
        if not record:
            raise ValueError("Record cannot be empty")
        
        try:
            data = self._read_data()
            
            # Add auto-generated ID if requested and not present
            if auto_id and 'id' not in record:
                record['id'] = str(uuid.uuid4())
            
            # Add timestamp
            record['created_at'] = datetime.now().isoformat()
            record['updated_at'] = datetime.now().isoformat()
            
            data.append(record)
            self._write_data(data)
            
            return record.get('id', str(len(data) - 1))
            
        except Exception as e:
            raise IOError(f"Failed to insert record: {e}")
    
    def read(self, record_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Read records from the JSON database.
        
        Args:
            record_id (Optional[str]): Specific record ID to retrieve
            filters (Optional[Dict[str, Any]]): Filters to apply
            
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Single record or list of records
            
        Raises:
            ValueError: If record not found
            IOError: If file operations fail
        """
        try:
            data = self._read_data()
            
            # Return specific record by ID
            if record_id:
                for record in data:
                    if record.get('id') == record_id:
                        return record
                raise ValueError(f"Record with ID '{record_id}' not found")
            
            # Apply filters if provided
            if filters:
                filtered_data = []
                for record in data:
                    match = True
                    for key, value in filters.items():
                        if key not in record or record[key] != value:
                            match = False
                            break
                    if match:
                        filtered_data.append(record)
                return filtered_data
            
            # Return all records
            return data
            
        except ValueError:
            raise
        except Exception as e:
            raise IOError(f"Failed to read records: {e}")
    
    def update(self, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record in the JSON database.
        
        Args:
            record_id (str): ID of the record to update
            updates (Dict[str, Any]): Fields to update
            
        Returns:
            Dict[str, Any]: Updated record
            
        Raises:
            ValueError: If record not found or updates invalid
            IOError: If file operations fail
        """
        if not isinstance(updates, dict):
            raise ValueError("Updates must be a dictionary")
        
        if not updates:
            raise ValueError("Updates cannot be empty")
        
        if not record_id:
            raise ValueError("Record ID is required")
        
        try:
            data = self._read_data()
            
            # Find and update the record
            for i, record in enumerate(data):
                if record.get('id') == record_id:
                    # Update fields
                    for key, value in updates.items():
                        record[key] = value
                    
                    # Update timestamp
                    record['updated_at'] = datetime.now().isoformat()
                    
                    data[i] = record
                    self._write_data(data)
                    return record
            
            raise ValueError(f"Record with ID '{record_id}' not found")
            
        except ValueError:
            raise
        except Exception as e:
            raise IOError(f"Failed to update record: {e}")
    
    def delete(self, record_id: str) -> bool:
        """
        Delete a record from the JSON database.
        
        Args:
            record_id (str): ID of the record to delete
            
        Returns:
            bool: True if record was deleted, False otherwise
            
        Raises:
            ValueError: If record ID is invalid
            IOError: If file operations fail
        """
        if not record_id:
            raise ValueError("Record ID is required")
        
        try:
            data = self._read_data()
            
            # Find and remove the record
            for i, record in enumerate(data):
                if record.get('id') == record_id:
                    del data[i]
                    self._write_data(data)
                    return True
            
            return False
            
        except Exception as e:
            raise IOError(f"Failed to delete record: {e}")
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records in the database.
        
        Args:
            filters (Optional[Dict[str, Any]]): Filters to apply
            
        Returns:
            int: Number of records
        """
        try:
            if filters:
                records = self.read(filters=filters)
                return len(records)
            else:
                data = self._read_data()
                return len(data)
        except Exception as e:
            raise IOError(f"Failed to count records: {e}")
    
    def clear(self) -> None:
        """
        Clear all records from the database.
        
        Raises:
            IOError: If file operations fail
        """
        try:
            self._write_data([])
        except Exception as e:
            raise IOError(f"Failed to clear database: {e}")
    
    @property
    def database_path(self) -> str:
        """Get the full path to the database file."""
        return self.file_path
    
    @property
    def database_name(self) -> str:
        """Get the database filename without path."""
        return os.path.basename(self.file_path)


# Convenience functions for simple operations
def create_database(file_path: str) -> JSONDatabase:
    """
    Create a new JSON database instance.
    
    Args:
        file_path (str): Database filename (will be placed in configured db directory)
        
    Returns:
        JSONDatabase: Database instance
    """
    return JSONDatabase(file_path)


def insert_record(file_path: str, record: Dict[str, Any], auto_id: bool = True) -> str:
    """
    Insert a record into a JSON file.
    
    Args:
        file_path (str): Database filename (will be placed in configured db directory)
        record (Dict[str, Any]): Record to insert
        auto_id (bool): Whether to auto-generate ID
        
    Returns:
        str: ID of inserted record
    """
    db = JSONDatabase(file_path)
    return db.insert(record, auto_id)


def read_records(file_path: str, record_id: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Read records from a JSON file.
    
    Args:
        file_path (str): Database filename (will be placed in configured db directory)
        record_id (Optional[str]): Specific record ID
        filters (Optional[Dict[str, Any]]): Filters to apply
        
    Returns:
        Union[Dict[str, Any], List[Dict[str, Any]]]: Records
    """
    db = JSONDatabase(file_path)
    return db.read(record_id, filters)


def update_record(file_path: str, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a record in a JSON file.
    
    Args:
        file_path (str): Database filename (will be placed in configured db directory)
        record_id (str): ID of record to update
        updates (Dict[str, Any]): Updates to apply
        
    Returns:
        Dict[str, Any]: Updated record
    """
    db = JSONDatabase(file_path)
    return db.update(record_id, updates)


def delete_record(file_path: str, record_id: str) -> bool:
    """
    Delete a record from a JSON file.
    
    Args:
        file_path (str): Database filename (will be placed in configured db directory)
        record_id (str): ID of record to delete
        
    Returns:
        bool: True if deleted, False otherwise
    """
    db = JSONDatabase(file_path)
    return db.delete(record_id)


def list_databases() -> List[str]:
    """
    List all database files in the configured directory.
    
    Returns:
        List[str]: List of database filenames
    """
    try:
        db_dir = config.db_directory
        if not os.path.exists(db_dir):
            return []
        
        extension = config.default_extension
        files = []
        for file in os.listdir(db_dir):
            if file.endswith(extension):
                files.append(file)
        
        return sorted(files)
    except Exception:
        return []


def get_database_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a database file.
    
    Args:
        file_path (str): Database filename
        
    Returns:
        Dict[str, Any]: Database information
    """
    try:
        # Get the full path without creating the database
        full_path = config.get_db_path(file_path)
        filename = os.path.basename(full_path)
        
        info = {
            "filename": filename,
            "full_path": full_path,
            "exists": os.path.exists(full_path),
            "record_count": 0,
            "file_size_bytes": 0,
            "created": None,
            "modified": None
        }
        
        if info["exists"]:
            stat = os.stat(full_path)
            info["file_size_bytes"] = stat.st_size
            info["created"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Only create database instance if file exists to get record count
            db = JSONDatabase(file_path)
            info["record_count"] = db.count()
        
        return info
    except Exception as e:
        return {
            "filename": file_path,
            "error": str(e),
            "exists": False
        } 