#!/usr/bin/env python3
"""
Tournament Processing Engine

Core processing logic for tournament data extraction and processing.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta

# Add project root to path for tournament_calendar imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Tournament calendar imports
from tournament_calendar.core.query_generator import QueryGenerator
from tournament_calendar.core.search_collector import SearchResultsCollector
from tournament_calendar.core.content_extractor import ContentExtractor
from tournament_calendar.core.data_processor import TournamentDataProcessor


class TournamentProcessingEngine:
    """Core engine for tournament data processing pipeline."""
    
    def __init__(self):
        """Initialize processing components."""
        self.query_generator: Optional[QueryGenerator] = None
        self.search_collector: Optional[SearchResultsCollector] = None
        self.content_extractor: Optional[ContentExtractor] = None
        self.data_processor: Optional[TournamentDataProcessor] = None
    
    def initialize_components(self) -> bool:
        """Initialize all processing components."""
        try:
            self.query_generator = QueryGenerator()
            self.search_collector = SearchResultsCollector()
            self.content_extractor = ContentExtractor()
            self.data_processor = TournamentDataProcessor()
            
            # Validate API keys
            if not self.search_collector.validate_api_key():
                raise Exception("Invalid Serper API key")
            
            if not self.content_extractor.validate_and_initialize():
                raise Exception("Invalid Firecrawl API key")
            
            return True
            
        except Exception as e:
            print(f"❌ Processing engine initialization error: {e}")
            return False
    
    def generate_sport_queries(self, sport: str) -> List[Dict[str, Any]]:
        """Generate search queries for a specific sport."""
        if not self.query_generator:
            raise Exception("Query generator not initialized")
        
        all_queries = self.query_generator.generate_all_queries(use_llm_enhancement=False)
        sport_queries = [q for q in all_queries if q.get('sport', '').lower() == sport.lower()]
        
        if not sport_queries:
            raise Exception(f"No queries available for sport: {sport}")
        
        return sport_queries
    
    def collect_search_results(self, queries: List[Dict[str, Any]], results_per_query: int = 8) -> List[Dict]:
        """Collect search results for multiple queries."""
        if not self.search_collector:
            raise Exception("Search collector not initialized")
        
        all_search_results = []
        
        for i, query_data in enumerate(queries, 1):
            query_text = query_data.get('query', str(query_data))
            print(f"   Query {i}/{len(queries)}: {query_text[:60]}...")
            
            results = self.search_collector.search_query(query_text, num_results=results_per_query)
            if results and 'organic' in results:
                search_results = results['organic']
                all_search_results.extend(search_results)
                print(f"   → Found {len(search_results)} results")
        
        return all_search_results
    
    def extract_tournaments(self, search_results: List[Dict], max_urls: Optional[int] = None) -> List[Dict]:
        """Extract tournaments from search results."""
        if not self.content_extractor:
            raise Exception("Content extractor not initialized")
        
        tournaments = self.content_extractor.extract_tournaments_from_search_results(
            search_results, 
            max_urls=max_urls
        )
        
        return tournaments or []
    
    def process_and_deduplicate(self, tournaments: List[Dict]) -> List[Dict]:
        """Process and deduplicate tournament data."""
        if not self.data_processor:
            raise Exception("Data processor not initialized")
        
        return self.data_processor.deduplicate_tournaments(tournaments)
    
    def get_component_status(self) -> Dict[str, bool]:
        """Get status of all processing components."""
        return {
            "query_generator": self.query_generator is not None,
            "search_collector": self.search_collector is not None,
            "content_extractor": self.content_extractor is not None,
            "data_processor": self.data_processor is not None
        }
