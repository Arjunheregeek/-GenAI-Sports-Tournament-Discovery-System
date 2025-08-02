"""
Configuration tests for Tournament Calendar System.

Tests the configuration management, validation, and API key handling.
"""

import pytest
import os
from unittest.mock import patch

from tournament_calendar.core.config import TournamentConfig, APIConfig, DatabaseConfig


class TestTournamentConfig:
    """Test the main configuration class."""
    
    def test_default_configuration(self):
        """Test that default configuration is loaded correctly."""
        config = TournamentConfig()
        
        # Test sports list
        assert len(config.SPORTS_LIST) == 12
        assert 'soccer' in config.SPORTS_LIST
        assert 'basketball' in config.SPORTS_LIST
        
        # Test levels list  
        assert len(config.LEVELS_LIST) == 12
        assert 'professional' in config.LEVELS_LIST
        assert 'amateur' in config.LEVELS_LIST
        
        # Test output fields
        assert len(config.OUTPUT_FIELDS) >= 8
        assert 'tournament_name' in config.OUTPUT_FIELDS
        assert 'start_date' in config.OUTPUT_FIELDS
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        config = TournamentConfig()
        
        # Mock missing API keys
        with patch.dict(os.environ, {}, clear=True):
            errors = config.validate_config()
            assert len(errors) > 0
            assert any('API key' in error for error in errors)
    
    def test_custom_configuration(self):
        """Test custom configuration loading."""
        custom_sports = ['tennis', 'golf']
        custom_levels = ['pro', 'amateur']
        
        config = TournamentConfig(
            sports_list=custom_sports,
            levels_list=custom_levels
        )
        
        assert config.SPORTS_LIST == custom_sports
        assert config.LEVELS_LIST == custom_levels


class TestAPIConfig:
    """Test API configuration."""
    
    def test_api_config_from_environment(self):
        """Test API config loads from environment variables."""
        test_keys = {
            'SERPER_API_KEY': 'test_serper_key',
            'FIRECRAWL_API_KEY': 'test_firecrawl_key', 
            'OPENAI_API_KEY': 'test_openai_key'
        }
        
        with patch.dict(os.environ, test_keys):
            api_config = APIConfig()
            
            assert api_config.serper_api_key == 'test_serper_key'
            assert api_config.firecrawl_api_key == 'test_firecrawl_key'
            assert api_config.openai_api_key == 'test_openai_key'
    
    def test_missing_api_keys(self):
        """Test behavior with missing API keys."""
        with patch.dict(os.environ, {}, clear=True):
            api_config = APIConfig()
            
            assert api_config.serper_api_key is None
            assert api_config.firecrawl_api_key is None
            assert api_config.openai_api_key is None
    
    def test_api_validation(self):
        """Test API key validation."""
        # Valid keys
        with patch.dict(os.environ, {
            'SERPER_API_KEY': 'valid_key',
            'FIRECRAWL_API_KEY': 'valid_key',
            'OPENAI_API_KEY': 'valid_key'
        }):
            api_config = APIConfig()
            errors = api_config.validate()
            assert len(errors) == 0
        
        # Missing keys
        with patch.dict(os.environ, {}, clear=True):
            api_config = APIConfig()
            errors = api_config.validate()
            assert len(errors) == 3


class TestDatabaseConfig:
    """Test database configuration."""
    
    def test_default_database_config(self):
        """Test default database configuration."""
        db_config = DatabaseConfig()
        
        assert db_config.host == 'localhost'
        assert db_config.port == 3306
        assert db_config.database == 'tournament_calendar'
        assert db_config.user == 'root'
    
    def test_database_config_from_environment(self):
        """Test database config from environment variables."""
        test_config = {
            'DB_HOST': 'test_host',
            'DB_PORT': '5432',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_pass'
        }
        
        with patch.dict(os.environ, test_config):
            db_config = DatabaseConfig()
            
            assert db_config.host == 'test_host'
            assert db_config.port == 5432
            assert db_config.database == 'test_db'
            assert db_config.user == 'test_user'
            assert db_config.password == 'test_pass'
    
    def test_database_validation(self):
        """Test database configuration validation."""
        # Valid config
        with patch.dict(os.environ, {'DB_PASSWORD': 'test_pass'}):
            db_config = DatabaseConfig()
            errors = db_config.validate()
            assert len(errors) == 0
        
        # Missing password
        with patch.dict(os.environ, {}, clear=True):
            db_config = DatabaseConfig()
            errors = db_config.validate()
            assert len(errors) == 1
            assert 'password' in errors[0].lower()


class TestIntegration:
    """Integration tests for configuration system."""
    
    def test_full_configuration_validation(self):
        """Test complete configuration validation."""
        # Mock complete environment
        complete_env = {
            'SERPER_API_KEY': 'test_serper',
            'FIRECRAWL_API_KEY': 'test_firecrawl',
            'OPENAI_API_KEY': 'test_openai',
            'DB_PASSWORD': 'test_password'
        }
        
        with patch.dict(os.environ, complete_env):
            config = TournamentConfig()
            errors = config.validate_config()
            assert len(errors) == 0
    
    def test_configuration_coverage(self):
        """Test that configuration covers all required combinations."""
        config = TournamentConfig()
        
        # Test coverage calculation
        total_combinations = len(config.SPORTS_LIST) * len(config.LEVELS_LIST)
        assert total_combinations == 144  # 12 sports × 12 levels
        
        # Test that all combinations are unique
        combinations = [
            (sport, level) 
            for sport in config.SPORTS_LIST 
            for level in config.LEVELS_LIST
        ]
        assert len(combinations) == len(set(combinations))
