#!/usr/bin/env python3
"""
Tournament Routes

Tournament search and processing endpoints.
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use relative imports for api modules
try:
    from ..models import APIResponse, ProcessingStatus, ProcessingType
    from ..utils import (
        handle_api_errors, log_request, validate_sport, 
        get_supported_sports, format_error_response
    )
    from ..services import TournamentService
except ImportError:
    # Fallback for when module is run directly
    from tournament_system.api.models import APIResponse, ProcessingStatus, ProcessingType
    from tournament_system.api.utils import (
        handle_api_errors, log_request, validate_sport, 
        get_supported_sports, format_error_response
    )
    from tournament_system.api.services import TournamentService

tournament_bp = Blueprint('tournament', __name__)


@tournament_bp.route('/search')
@log_request
@handle_api_errors
def search_tournaments():
    """
    Quick tournament search endpoint.
    
    Query Parameters:
    - sport: The sport to search for (required)
    - level: Tournament level (required, currently only 'International' supported)
    - export: Whether to export results to files (optional, defaults to 'false')
    
    Returns:
        JSON response with tournament search results
    """
    from flask import g, current_app
    
    # Get tournament service instance from app context
    tournament_service = getattr(g, 'tournament_service', None) or getattr(current_app, 'tournament_service', None)
    
    if not tournament_service or not tournament_service.initialized:
        return format_error_response("Tournament service not available", 503)
    
    # Get and validate parameters
    sport = request.args.get('sport', '').strip()
    level = request.args.get('level', '').strip()
    export_files = request.args.get('export', 'false').lower() == 'true'
    
    # Validate required parameters
    if not sport:
        return format_error_response("Missing required parameter: sport", 400)
    
    if not level:
        return format_error_response("Missing required parameter: level", 400)
    
    # Validate sport
    if not validate_sport(sport):
        return jsonify({
            "status": ProcessingStatus.ERROR.value,
            "error": "Sport not supported",
            "message": f"Sport '{sport}' is not supported",
            "supported_sports": get_supported_sports()
        }), 400
    
    # Validate level (currently only International supported)
    if level.lower() != 'international':
        return format_error_response(
            f"Level '{level}' not supported. Currently only 'International' is supported.", 
            400
        )
    
    try:
        # Process quick search
        tournaments, metadata, export_info = tournament_service.process_quick_search(
            sport=sport,
            level=level,
            export_files=export_files
        )
        
        # Create response
        response = APIResponse(
            status=ProcessingStatus.SUCCESS,
            message=f"Found {len(tournaments)} {sport} tournaments",
            sport=sport,
            processing_type=ProcessingType.QUICK_SEARCH,
            tournaments=tournaments,
            metadata=metadata,
            export_info=export_info
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        return format_error_response(str(e), 500)


@tournament_bp.route('/comprehensive')
@log_request
@handle_api_errors
def comprehensive_processing():
    """
    Comprehensive tournament processing endpoint - replicates main.py functionality.
    
    Query Parameters:
    - sport: The sport to search for (optional, defaults to 'Cricket')
    - export: Whether to export results to files (optional, defaults to 'true')
    
    Returns:
        JSON response with comprehensive tournament results and file exports
    """
    from flask import g, current_app
    
    # Get tournament service instance from app context
    tournament_service = getattr(g, 'tournament_service', None) or getattr(current_app, 'tournament_service', None)
    
    if not tournament_service or not tournament_service.initialized:
        return format_error_response("Tournament service not available", 503)
    
    # Get and validate parameters
    sport = request.args.get('sport', 'Cricket').strip()
    export_files = request.args.get('export', 'true').lower() == 'true'
    
    # Validate sport
    if not validate_sport(sport):
        return jsonify({
            "status": ProcessingStatus.ERROR.value,
            "error": "Sport not supported for comprehensive processing",
            "message": f"No queries available for sport: {sport}",
            "supported_sports": get_supported_sports()
        }), 400
    
    try:
        # Process comprehensive search
        tournaments, metadata, export_info, summary = tournament_service.process_comprehensive_tournaments(
            sport=sport,
            export_files=export_files
        )
        
        # Create response
        response = APIResponse(
            status=ProcessingStatus.SUCCESS,
            message=f"Comprehensive processing completed: {len(tournaments)} {sport} tournaments found and processed",
            sport=sport,
            processing_type=ProcessingType.COMPREHENSIVE,
            tournaments=tournaments,
            metadata=metadata,
            export_info=export_info,
            summary=summary
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        return format_error_response(str(e), 500)
