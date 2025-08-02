#!/usr/bin/env python3
"""
Health Check Routes

Health check and system status endpoints.
"""

import sys
from pathlib import Path
from flask import Blueprint, jsonify
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use relative imports for api modules
try:
    from ..config import APIServerConfig
    from ..models import HealthCheckResponse
    from ..utils import handle_api_errors, log_request
    from ..services import TournamentService
except ImportError:
    # Fallback for when module is run directly
    from api.config import APIServerConfig
    from api.models import HealthCheckResponse
    from api.utils import handle_api_errors, log_request
    from api.services import TournamentService

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
@log_request
@handle_api_errors
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status
    """
    from flask import g, current_app
    
    # Get tournament service instance from app context
    tournament_service = getattr(g, 'tournament_service', None) or getattr(current_app, 'tournament_service', None)
    
    if not tournament_service:
        return jsonify({
            "status": "error",
            "message": "Tournament service not available",
            "timestamp": datetime.now().isoformat()
        }), 503
    
    # Get service status
    services = tournament_service.get_service_status()
    
    # Get configuration
    config = APIServerConfig.from_env()
    
    # Create health check response
    health_response = HealthCheckResponse(
        status="healthy" if all(services.values()) else "degraded",
        timestamp=datetime.now().isoformat(),
        version="3.0.0",
        services=services,
        configuration=config.to_dict()
    )
    
    status_code = 200 if all(services.values()) else 503
    return jsonify(health_response.to_dict()), status_code
