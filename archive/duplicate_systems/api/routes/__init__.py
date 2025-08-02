#!/usr/bin/env python3
"""
API Routes Package

Route blueprints for the API endpoints.
"""

from .health import health_bp
from .docs import docs_bp
from .tournaments import tournament_bp

__all__ = ['health_bp', 'docs_bp', 'tournament_bp']
