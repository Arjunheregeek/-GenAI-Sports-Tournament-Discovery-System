#!/usr/bin/env python3
"""
Flask Application Factory

Creates and configures the Flask application with all routes and services.
"""

import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use relative imports for api modules
try:
    from .config import APIServerConfig, validate_api_config
    from .services import TournamentService
    from .routes import health_bp, docs_bp, tournament_bp
except ImportError:
    # Fallback for when module is run directly
    from tournament_system.api.config import APIServerConfig, validate_api_config
    from tournament_system.api.services import TournamentService
    from tournament_system.api.routes import health_bp, docs_bp, tournament_bp


def create_app(config: APIServerConfig = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: API server configuration
        
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Use provided config or create from environment
    if config is None:
        config = APIServerConfig.from_env()
    
    # Configure app
    app.config.update(config.to_dict())
    
    # Setup CORS
    CORS(app, origins=config.cors_origins)
    
    # Initialize tournament service
    tournament_service = TournamentService()
    
    # Store service instance in app context for access in routes
    app.tournament_service = tournament_service
    
    # Register blueprints
    app.register_blueprint(docs_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(tournament_bp)
    
    # Store tournament service reference for route access
    # This is a cleaner way to provide service access to routes
    @app.before_request
    def inject_tournament_service():
        from flask import g
        g.tournament_service = tournament_service
    
    return app


def initialize_app(app: Flask) -> bool:
    """
    Initialize the application and all services.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if initialization successful, False otherwise
    """
    print("🚀 Starting Tournament Calendar API Server...")
    print("=" * 60)
    
    # Validate API configuration
    if not validate_api_config():
        print("❌ API configuration validation failed")
        return False
    
    # Initialize tournament service
    if not app.tournament_service.initialize():
        print("❌ Tournament service initialization failed")
        return False
    
    print("✅ API Server initialized successfully!")
    print("📡 Ready to process tournament requests")
    print("=" * 60)
    
    return True
