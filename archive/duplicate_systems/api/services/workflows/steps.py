#!/usr/bin/env python3
"""
Workflow Steps Module

Individual workflow steps for tournament processing.
"""

from typing import List, Dict, Any


class WorkflowSteps:
    """Individual workflow steps that can be composed into larger workflows."""
    
    @staticmethod
    def generate_queries(processing_engine, sport: str) -> List[Dict[str, Any]]:
        """Step 1: Generate sport-specific queries."""
        return processing_engine.generate_sport_queries(sport)
    
    @staticmethod
    def collect_results(processing_engine, queries: List[Dict], results_per_query: int = 8) -> List[Dict]:
        """Step 2: Collect search results."""
        return processing_engine.collect_search_results(queries, results_per_query)
    
    @staticmethod
    def extract_tournaments(processing_engine, search_results: List[Dict]) -> List[Dict]:
        """Step 3: Extract tournaments from search results."""
        return processing_engine.extract_tournaments(search_results, max_urls=None)
    
    @staticmethod
    def process_tournaments(processing_engine, tournaments: List[Dict]) -> List[Dict]:
        """Step 4: Process and deduplicate tournaments."""
        return processing_engine.process_and_deduplicate(tournaments)
    
    @staticmethod
    def filter_tournaments(filter_service, tournaments: List[Dict], level: str = None) -> List[Dict]:
        """Step 5: Filter and sort tournaments."""
        filtered = filter_service.filter_recent_and_future_tournaments(tournaments)
        if level:
            filtered = filter_service.filter_by_level(filtered, level)
        return filter_service.sort_tournaments_by_date(filtered)
    
    @staticmethod
    def export_results(export_manager, tournaments: List[Dict], filename: str, export_enabled: bool) -> Any:
        """Step 6: Export tournament results."""
        return export_manager.export_tournaments(tournaments, filename, export_enabled)
