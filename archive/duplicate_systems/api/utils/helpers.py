#!/usr/bin/env python3
"""
API Utilities Module

Helper functions and utilities for the API.
"""

from typing import Dict, Any, List, Optional
from flask import request, jsonify
from functools import wraps
import time

from api.models import APIResponse, ProcessingStatus


def validate_request_params(required_params: List[str], optional_params: Dict[str, Any] = None):
    """
    Decorator to validate request parameters.
    
    Args:
        required_params: List of required parameter names
        optional_params: Dict of optional parameters with default values
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check required parameters
            missing_params = []
            for param in required_params:
                if not request.args.get(param):
                    missing_params.append(param)
            
            if missing_params:
                response = APIResponse(
                    status=ProcessingStatus.ERROR,
                    message=f"Missing required parameters: {', '.join(missing_params)}",
                    error=f"Required parameters: {', '.join(required_params)}"
                )
                return jsonify(response.to_dict()), 400
            
            # Add optional parameters with defaults
            if optional_params:
                for param, default_value in optional_params.items():
                    if param not in kwargs:
                        kwargs[param] = request.args.get(param, default_value)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_api_errors(func):
    """
    Decorator to handle API errors consistently.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ API Error in {func.__name__}: {e}")
            response = APIResponse(
                status=ProcessingStatus.ERROR,
                message=f"Internal server error in {func.__name__}",
                error=str(e)
            )
            return jsonify(response.to_dict()), 500
    return wrapper


def log_request(func):
    """
    Decorator to log API requests.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"🌐 API Request: {request.method} {request.path}")
        print(f"📋 Parameters: {dict(request.args)}")
        
        result = func(*args, **kwargs)
        
        processing_time = time.time() - start_time
        print(f"⏱️ Request completed in {processing_time:.2f} seconds")
        
        return result
    return wrapper


def format_error_response(error_message: str, status_code: int = 500) -> tuple:
    """
    Format a standardized error response.
    
    Args:
        error_message: Error message to include
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    response = APIResponse(
        status=ProcessingStatus.ERROR,
        message="Request failed",
        error=error_message
    )
    return jsonify(response.to_dict()), status_code


def format_success_response(
    message: str,
    data: Dict[str, Any] = None,
    status_code: int = 200
) -> tuple:
    """
    Format a standardized success response.
    
    Args:
        message: Success message
        data: Additional data to include
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    response_data = {
        "status": ProcessingStatus.SUCCESS.value,
        "message": message
    }
    
    if data:
        response_data.update(data)
    
    return jsonify(response_data), status_code


def get_supported_sports() -> List[str]:
    """Get list of supported sports."""
    return [
        "Cricket", "Football", "Basketball", "Tennis", "Badminton", 
        "Swimming", "Running", "Cycling", "Chess", "Table Tennis", 
        "Kabaddi", "Yoga", "Gym"
    ]


def validate_sport(sport: str) -> bool:
    """
    Validate if sport is supported.
    
    Args:
        sport: Sport name to validate
        
    Returns:
        True if sport is supported, False otherwise
    """
    return sport.lower() in [s.lower() for s in get_supported_sports()]


def create_api_documentation() -> Dict[str, Any]:
    """Create API documentation structure."""
    return {
        "title": "Tournament Calendar API",
        "version": "3.0.0",
        "description": "Comprehensive API for tournament data extraction and processing",
        "endpoints": {
            "/": {
                "method": "GET",
                "description": "API documentation",
                "parameters": {}
            },
            "/health": {
                "method": "GET", 
                "description": "Health check endpoint",
                "parameters": {}
            },
            "/search": {
                "method": "GET",
                "description": "Quick tournament search",
                "parameters": {
                    "sport": {
                        "required": True,
                        "description": "Sport name",
                        "example": "Cricket"
                    },
                    "level": {
                        "required": True,
                        "description": "Tournament level",
                        "example": "International"
                    },
                    "export": {
                        "required": False,
                        "description": "Export results to files",
                        "default": "false"
                    }
                }
            },
            "/comprehensive": {
                "method": "GET",
                "description": "Comprehensive tournament processing (full main.py functionality)",
                "parameters": {
                    "sport": {
                        "required": False,
                        "description": "Sport name",
                        "default": "Cricket"
                    },
                    "export": {
                        "required": False,
                        "description": "Export results to files",
                        "default": "true"
                    }
                }
            }
        },
        "supported_sports": get_supported_sports(),
        "response_format": {
            "status": "success|error",
            "message": "Response message",
            "sport": "Sport name",
            "tournaments": "Array of tournament objects",
            "metadata": "Processing metadata",
            "export_info": "File export information"
        }
    }
