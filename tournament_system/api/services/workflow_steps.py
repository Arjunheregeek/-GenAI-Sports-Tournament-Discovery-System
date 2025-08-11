#!/usr/bin/env python3
"""
Workflow Steps Module

Individual workflow steps for tournament processing.
"""

from typing import List, Dict, Any
from datetime import datetime


class WorkflowStep:
    """Base class for workflow steps."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time: datetime = None
        self.end_time: datetime = None
    
    def start(self):
        """Mark step as started."""
        self.start_time = datetime.now()
        print(f"🔄 {self.name}: {self.description}...")
    
    def complete(self, result_count: int = None):
        """Mark step as completed."""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if result_count is not None:
            print(f"✅ {self.name} completed: {result_count} items ({duration:.2f}s)")
        else:
            print(f"✅ {self.name} completed ({duration:.2f}s)")
    
    def get_duration(self) -> float:
        """Get step duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class QueryGenerationStep(WorkflowStep):
    """Step for generating search queries."""
    
    def __init__(self):
        super().__init__("STEP 1", "Generating search queries")
    
    def execute(self, processing_engine, sport: str) -> List[Dict[str, Any]]:
        """Execute query generation step."""
        self.start()
        sport_queries = processing_engine.generate_sport_queries(sport)
        self.complete(len(sport_queries))
        return sport_queries


class SearchCollectionStep(WorkflowStep):
    """Step for collecting search results."""
    
    def __init__(self):
        super().__init__("STEP 2", "Collecting search results")
    
    def execute(self, processing_engine, queries: List[Dict], results_per_query: int = 8) -> List[Dict]:
        """Execute search collection step."""
        self.start()
        all_search_results = processing_engine.collect_search_results(queries, results_per_query)
        self.complete(len(all_search_results))
        return all_search_results


class TournamentExtractionStep(WorkflowStep):
    """Step for extracting tournaments."""
    
    def __init__(self):
        super().__init__("STEP 3", "Extracting tournaments from URLs")
    
    def execute(self, processing_engine, search_results: List[Dict], max_urls: int = None) -> List[Dict]:
        """Execute tournament extraction step."""
        self.start()
        tournaments = processing_engine.extract_tournaments(search_results, max_urls)
        self.complete(len(tournaments))
        return tournaments


class DeduplicationStep(WorkflowStep):
    """Step for processing and deduplicating tournaments."""
    
    def __init__(self):
        super().__init__("STEP 4", "Processing and deduplicating")
    
    def execute(self, processing_engine, tournaments: List[Dict]) -> List[Dict]:
        """Execute deduplication step."""
        self.start()
        unique_tournaments = processing_engine.process_and_deduplicate(tournaments)
        self.complete(len(unique_tournaments))
        return unique_tournaments


class FilteringStep(WorkflowStep):
    """Step for filtering relevant tournaments."""
    
    def __init__(self):
        super().__init__("STEP 5", "Filtering relevant tournaments")
    
    def execute(self, filter_service, tournaments: List[Dict], level: str = None) -> List[Dict]:
        """Execute filtering step."""
        self.start()
        
        # Filter by date
        relevant_tournaments = filter_service.filter_recent_and_future_tournaments(tournaments)
        
        # Filter by level if specified
        if level:
            relevant_tournaments = filter_service.filter_by_level(relevant_tournaments, level)
        
        # Sort by date
        relevant_tournaments = filter_service.sort_tournaments_by_date(relevant_tournaments)
        
        self.complete(len(relevant_tournaments))
        return relevant_tournaments


class ExportStep(WorkflowStep):
    """Step for exporting tournament data."""
    
    def __init__(self):
        super().__init__("STEP 6", "Exporting tournament data")
    
    def execute(self, export_manager, tournaments: List[Dict], filename_prefix: str, export_enabled: bool):
        """Execute export step."""
        if not export_enabled or not tournaments:
            return export_manager.export_tournaments(tournaments, filename_prefix, False)
        
        self.start()
        export_info = export_manager.export_tournaments(tournaments, filename_prefix, export_enabled)
        self.complete()
        return export_info
