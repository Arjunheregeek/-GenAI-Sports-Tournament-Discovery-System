#!/usr/bin/env python3
"""
Documentation Routes

API documentation and information endpoints.
"""

import sys
from pathlib import Path
from flask import Blueprint, jsonify

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use relative imports for api modules
try:
    from ..utils import handle_api_errors, log_request, create_api_documentation
except ImportError:
    # Fallback for when module is run directly
    from tournament_system.api.utils import handle_api_errors, log_request, create_api_documentation

docs_bp = Blueprint('docs', __name__)


@docs_bp.route('/')
@log_request
@handle_api_errors
def api_documentation():
    """
    API documentation endpoint.
    
    Returns:
        JSON response with API documentation
    """
    documentation = create_api_documentation()
    return jsonify(documentation), 200
