"""
Configuration settings for the Tournament Calendar system.
Contains all sports, levels, and database schema definitions.
"""

import os
from typing import List, Dict, Any

# All sports to cover as per assignment
SPORTS_LIST = [
    "Cricket"
]

# All levels to cover as per assignment
LEVELS_LIST = [
    "International"
]

# Output format fields as per assignment requirements
OUTPUT_FIELDS = [
    "tournament_name",      # Tournament Name
    "level",               # Level  
    "start_date",          # Start Date
    "end_date",           # End Date
    "official_url",       # Tournament Official URL
    "streaming_links",    # Streaming Partners/Links (array)
    "image_url",         # Tournament Image
    "summary"            # Summary of Tournament (max 50 words)
]

# Additional fields for internal use
INTERNAL_FIELDS = [
    "sport",             # Sport category
    "source_url",        # Source URL where data was found
    "extraction_date",   # When the data was extracted
    "confidence_score"   # AI confidence in extraction accuracy
]

# Database schema
DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_name TEXT NOT NULL,
    sport TEXT NOT NULL,
    level TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    official_url TEXT,
    streaming_links TEXT,  -- JSON array as text
    image_url TEXT,
    summary TEXT,
    source_url TEXT,
    extraction_date TEXT,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# API Configuration
class APIConfig:
    """API configuration settings."""
    
    def __init__(self):
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        
        # API endpoints
        self.serper_base_url = "https://google.serper.dev/search"
        self.firecrawl_base_url = "https://api.firecrawl.dev/v0"
        
        # Rate limiting settings
        self.serper_rate_limit = 1.0  # seconds between requests
        self.openai_rate_limit = 0.5
        self.firecrawl_rate_limit = 2.0
        
        # Request settings
        self.request_timeout = 30
        self.max_retries = 3

# Database Configuration
class DatabaseConfig:
    """Database configuration settings."""
    
    def __init__(self):
        # MySQL Configuration (primary)
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'tournament_calendar')
        self.port = int(os.getenv('DB_PORT', 3306))
        
        # SQLite Configuration (fallback)
        self.database_file = "tournament_calendar.db"
        self.backup_directory = "backups"
        self.max_backup_files = 10
        
        # Connection settings
        self.connection_timeout = 30
        self.pool_size = 5
        self.max_overflow = 10

# System Configuration
class SystemConfig:
    """System-wide configuration settings."""
    
    def __init__(self):
        self.log_level = "INFO"
        self.log_file = "tournament_calendar.log"
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        
        # Processing settings
        self.batch_size = 10
        self.max_concurrent_requests = 5
        self.enable_caching = True
        self.cache_duration = 3600  # 1 hour in seconds

def get_config() -> Dict[str, Any]:
    """Get complete configuration as a dictionary."""
    return {
        'sports': SPORTS_LIST,
        'levels': LEVELS_LIST,
        'output_fields': OUTPUT_FIELDS,
        'internal_fields': INTERNAL_FIELDS,
        'database_schema': DATABASE_SCHEMA,
        'api': APIConfig(),
        'database': DatabaseConfig(),
        'system': SystemConfig()
    }

def validate_config() -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []
    
    # Check required environment variables
    required_env_vars = ['SERPER_API_KEY', 'OPENAI_API_KEY', 'FIRECRAWL_API_KEY']
    for env_var in required_env_vars:
        if not os.getenv(env_var):
            errors.append(f"Missing required environment variable: {env_var}")
    
    # Check sports and levels lists
    if not SPORTS_LIST:
        errors.append("SPORTS_LIST cannot be empty")
    
    if not LEVELS_LIST:
        errors.append("LEVELS_LIST cannot be empty")
    
    if not OUTPUT_FIELDS:
        errors.append("OUTPUT_FIELDS cannot be empty")
    
    return errors

if __name__ == "__main__":
    print("✅ Configuration loaded successfully")
    print(f"📊 Sports to cover: {len(SPORTS_LIST)}")
    print(f"🏆 Levels to cover: {len(LEVELS_LIST)}")
    print(f"📋 Output fields: {len(OUTPUT_FIELDS)}")
    
    # Validate configuration
    errors = validate_config()
    if errors:
        print("\n❌ Configuration errors found:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuration validation passed")
