"""
Tournament System - Clean, Essential Package

A comprehensive, organized system for tournament data extraction and processing.
Combines the best of both API server and batch processing approaches.
"""

__version__ = "4.0.0"
__author__ = "Tournament System"
__description__ = "Essential tournament data extraction system"

from .core.config import APIConfig
from .api import create_app

__all__ = ['APIConfig', 'create_app']
