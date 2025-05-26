import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for JSON CRUD operations."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one config instance."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_file: str = "settings.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str): Path to the configuration file
        """
        if self._config is None:
            self.config_file = config_file
            self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            else:
                # Use default configuration if file doesn't exist
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_file}: {e}")
            self._config = self._get_default_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config file {self.config_file}: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "database": {
                "directory": "db",
                "auto_create_directory": True,
                "default_file_extension": ".json",
                "backup_enabled": False,
                "backup_directory": "db/backups"
            },
            "logging": {
                "enabled": False,
                "level": "INFO",
                "file": "db/crud.log"
            },
            "performance": {
                "cache_enabled": False,
                "max_file_size_mb": 10,
                "pretty_print": True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'database.directory')
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'database.directory')
            value (Any): Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    @property
    def db_directory(self) -> str:
        """Get the database directory path."""
        return self.get('database.directory', 'db')
    
    @db_directory.setter
    def db_directory(self, value: str) -> None:
        """Set the database directory path."""
        self.set('database.directory', value)
    
    @property
    def auto_create_directory(self) -> bool:
        """Check if directories should be auto-created."""
        return self.get('database.auto_create_directory', True)
    
    @property
    def default_extension(self) -> str:
        """Get the default file extension."""
        return self.get('database.default_file_extension', '.json')
    
    @property
    def pretty_print(self) -> bool:
        """Check if JSON should be pretty printed."""
        return self.get('performance.pretty_print', True)
    
    def get_db_path(self, filename: str) -> str:
        """
        Get full database file path.
        
        Args:
            filename (str): Database filename
            
        Returns:
            str: Full path to database file
        """
        # Ensure filename has correct extension
        if not filename.endswith(self.default_extension):
            filename += self.default_extension
        
        # Create full path
        db_path = os.path.join(self.db_directory, filename)
        
        # Create directory if it doesn't exist and auto_create is enabled
        if self.auto_create_directory:
            os.makedirs(self.db_directory, exist_ok=True)
        
        return db_path
    
    def ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        if self.auto_create_directory:
            os.makedirs(self.db_directory, exist_ok=True)
            
            # Also create backup directory if backup is enabled
            if self.get('database.backup_enabled', False):
                backup_dir = self.get('database.backup_directory', 'db/backups')
                os.makedirs(backup_dir, exist_ok=True)


# Global config instance
config = Config() 