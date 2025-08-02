#!/usr/bin/env python3
"""
Tournament Calendar API Package

A modular Flask API server for tournament data extraction and processing.
"""

__version__ = "3.0.0"
__author__ = "Tournament Calendar System"  
__description__ = "Comprehensive API for tournament data extraction"

# Import the main create_app function from app.py
from .app import create_app, initialize_app

# Export the functions for external use
__all__ = ['create_app', 'initialize_app']
