"""
Core Configuration Module for Tournament Calendar System

This module contains all configuration settings, constants, and 
shared utilities used across the tournament collection system.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API configuration settings."""
    serper_api_key: str
    firecrawl_api_key: str
    openai_api_key: str
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create API config from environment variables."""
        return cls(
            serper_api_key=os.getenv('SERPER_API_KEY', ''),
            firecrawl_api_key=os.getenv('FIRECRAWL_API_KEY', ''),
            openai_api_key=os.getenv('OPENAI_API_KEY', '')
        )

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    user: str
    password: str
    database: str
    port: int
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables."""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'tournament_calendar'),
            port=int(os.getenv('DB_PORT', 3306))
        )

class TournamentConfig:
    """Main configuration class for the tournament calendar system."""
    
    # Sports Coverage (12 Sports)
    SPORTS_LIST = [
        "Cricket",
        "Football", 
        "Badminton",
        "Running",
        "Gym",
        "Cycling",
        "Swimming",
        "Kabaddi",
        "Yoga",
        "Basketball",
        "Chess",
        "Table Tennis"
    ]
    
    # Competition Levels (12 Levels)
    LEVELS_LIST = [
        "Corporate",
        "School",
        "College", 
        "University",
        "Club",
        "Academy",
        "District",
        "State",
        "Zonal",
        "Regional",
        "National",
        "International"
    ]
    
    # Required Output Fields
    OUTPUT_FIELDS = [
        "tournament_name",
        "level",
        "dates",
        "tournament_url",
        "streaming_links",
        "images",
        "summary"
    ]
    
    # Extended Fields for Database
    EXTENDED_FIELDS = [
        "registration_deadline",
        "entry_fee",
        "contact_info",
        "eligibility",
        "prizes",
        "venue"
    ]
    
    # API Rate Limits and Settings
    API_SETTINGS = {
        'serper': {
            'rate_limit_delay': 1.0,
            'max_retries': 3,
            'timeout': 30
        },
        'firecrawl': {
            'rate_limit_delay': 2.0,
            'max_retries': 3,
            'timeout': 60
        },
        'openai': {
            'rate_limit_delay': 1.0,
            'max_retries': 3,
            'model': 'gpt-3.5-turbo',
            'max_tokens': 1500,
            'temperature': 0.1
        }
    }
    
    # Quality Thresholds
    QUALITY_THRESHOLDS = {
        'min_content_length': 100,
        'max_content_length': 50000,
        'min_confidence_score': 0.4,
        'high_confidence_threshold': 0.7
    }
    
    # High Priority Domains for Tournament Information
    HIGH_PRIORITY_DOMAINS = [
        'gov.in', 'edu', 'bcci.tv', 'aiff.in', 'hockeyindia.org',
        'badmintonindia.org', 'tabletennis.org.in', 'aainet.org'
    ]
    
    # Medium Priority Domains
    MEDIUM_PRIORITY_DOMAINS = [
        'sportskeeda.com', 'espncricinfo.com', 'olympics.com',
        'sportstar.thehindu.com', 'indianexpress.com'
    ]
    
    # Database Schema Configuration
    DATABASE_SCHEMA = {
        'tournaments_table': {
            'name': 'tournaments',
            'indexes': [
                'idx_sport', 'idx_level', 'idx_dates', 'idx_venue',
                'idx_confidence', 'idx_created', 'idx_search'
            ]
        },
        'sports_table': {
            'name': 'sports',
            'reference_data': True
        },
        'levels_table': {
            'name': 'levels', 
            'reference_data': True
        },
        'extraction_log_table': {
            'name': 'extraction_log',
            'tracking': True
        }
    }
    
    # Output Directory Configuration
    OUTPUT_DIRECTORIES = {
        'final_output': 'final_output',
        'intermediate_data': 'data',
        'logs': 'logs',
        'cache': 'cache'
    }
    
    def __init__(self):
        """Initialize configuration with API and database settings."""
        self.api_config = APIConfig.from_env()
        self.database_config = DatabaseConfig.from_env()
        
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Check API keys
        if not self.api_config.serper_api_key:
            errors.append("SERPER_API_KEY not configured")
        if not self.api_config.firecrawl_api_key:
            errors.append("FIRECRAWL_API_KEY not configured")
        if not self.api_config.openai_api_key:
            errors.append("OPENAI_API_KEY not configured")
            
        # Check database config
        if not self.database_config.password:
            errors.append("Database password not configured")
            
        return errors
    
    def get_all_sport_level_combinations(self) -> List[tuple]:
        """Get all combinations of sports and levels."""
        combinations = []
        for sport in self.SPORTS_LIST:
            for level in self.LEVELS_LIST:
                combinations.append((sport, level))
        return combinations
    
    def get_output_fields_schema(self) -> Dict[str, str]:
        """Get the schema for output fields."""
        return {
            "tournament_name": "Full tournament name",
            "level": "Competition level (Corporate/School/College/etc.)",
            "dates": "Tournament dates (start - end or single date)",
            "tournament_url": "Official tournament webpage URL",
            "streaming_links": "Live streaming/broadcast URLs (comma-separated)",
            "images": "Tournament poster/logo image URLs (comma-separated)",
            "summary": "Brief tournament description"
        }

# Global configuration instance
config = TournamentConfig()
