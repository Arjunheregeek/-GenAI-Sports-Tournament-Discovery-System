#!/usr/bin/env python3
"""
Tournament Calendar API Package

A modular Flask API server for tournament data extraction and processing.
"""

__version__ = "3.0.0"
__author__ = "Tournament Calendar System"  
__description__ = "Comprehensive API for tournament data extraction"

from flask import Flask
from flask_cors import CORS


def create_app(config_name='default'):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app)
    
    # Register blueprints
    try:
        from .routes.tournament_routes import tournament_bp
        from .routes.system_routes import system_bp
        
        app.register_blueprint(tournament_bp, url_prefix='/api/tournaments')
        app.register_blueprint(system_bp, url_prefix='/api/system')
        
    except ImportError as e:
        print(f"Warning: Could not register routes: {e}")
    
    @app.route('/')
    def index():
        """API root endpoint."""
        return {
            "message": "Tournament Calendar API",
            "version": __version__,
            "status": "active"
        }
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {"status": "healthy", "version": __version__}
    
    return app
