#!/usr/bin/env python3
"""
API Configuration Module

Handles API server configuration, environment variables, and settings.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class APIServerConfig:
    """API Server configuration settings."""
    
    # Server settings
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    
    # API settings
    max_results_per_query: int = 8
    max_concurrent_requests: int = 10
    request_timeout: int = 300  # 5 minutes
    
    # Processing settings
    enable_exports: bool = True
    export_directory: str = "final_output"
    
    # CORS settings
    cors_origins: str = "*"
    
    @classmethod
    def from_env(cls) -> 'APIServerConfig':
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv('API_HOST', 'localhost'),
            port=int(os.getenv('API_PORT', '8000')),
            debug=os.getenv('API_DEBUG', 'false').lower() == 'true',
            max_results_per_query=int(os.getenv('MAX_RESULTS_PER_QUERY', '8')),
            max_concurrent_requests=int(os.getenv('MAX_CONCURRENT_REQUESTS', '10')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '300')),
            enable_exports=os.getenv('ENABLE_EXPORTS', 'true').lower() == 'true',
            export_directory=os.getenv('EXPORT_DIRECTORY', 'final_output'),
            cors_origins=os.getenv('CORS_ORIGINS', '*')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'debug': self.debug,
            'max_results_per_query': self.max_results_per_query,
            'max_concurrent_requests': self.max_concurrent_requests,
            'request_timeout': self.request_timeout,
            'enable_exports': self.enable_exports,
            'export_directory': self.export_directory,
            'cors_origins': self.cors_origins
        }


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def validate_api_config() -> bool:
    """Validate API configuration and dependencies."""
    try:
        # Check required environment variables
        required_vars = ['SERPER_API_KEY', 'FIRECRAWL_API_KEY', 'OPENAI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Validate export directory
        config = APIServerConfig.from_env()
        export_path = get_project_root() / config.export_directory
        export_path.mkdir(exist_ok=True)
        
        print("✅ API configuration validated successfully")
        return True
        
    except Exception as e:
        print(f"❌ API configuration validation failed: {e}")
        return False
