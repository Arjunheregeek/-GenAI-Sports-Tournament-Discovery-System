"""
GenAI Tournament Calendar Data Collection System

A comprehensive system for collecting tournament information across
multiple sports and competition levels using AI-powered web scraping.

Version: 1.0.0
Author: GenAI Tournament Calendar Team
"""

__version__ = "1.0.0"
__author__ = "GenAI Tournament Calendar Team"

from .core.config import TournamentConfig
from .core.pipeline import TournamentPipeline

__all__ = ["TournamentConfig", "TournamentPipeline"]
