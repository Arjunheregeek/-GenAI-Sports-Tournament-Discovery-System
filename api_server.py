#!/usr/bin/env python3
"""
Tournament Calendar API Server

A simple Flask API server to handle frontend requests and integrate 
with the existing tournament extraction system.

Endpoints:
- GET /search?sport=<sport>&level=<level> - Search tournaments
- GET /health - Health check
- GET / - API documentation

Usage:
    python api_server.py

Requirements:
    pip install flask flask-cors
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, date, timedelta

# Flask imports
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import your existing modules
from tournament_calendar.core.config import APIConfig, validate_config
from tournament_calendar.core.query_generator import QueryGenerator
from tournament_calendar.core.search_collector import SearchResultsCollector
from tournament_calendar.core.content_extractor import ContentExtractor
from tournament_calendar.core.data_processor import TournamentDataProcessor

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global variables
query_generator = None
search_collector = None
content_extractor = None
data_processor = None


def initialize_services():
    """Initialize all tournament extraction services."""
    global query_generator, search_collector, content_extractor, data_processor
    
    try:
        # Validate configuration
        validate_config()
        
        # Initialize services
        query_generator = QueryGenerator()
        search_collector = SearchResultsCollector()
        content_extractor = ContentExtractor()
        data_processor = TournamentDataProcessor()
        
        # Validate API keys
        if not search_collector.validate_api_key():
            raise Exception("Invalid Serper API key")
        
        if not content_extractor.validate_and_initialize():
            raise Exception("Invalid Firecrawl API key")
        
        print("✅ All services initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        return False


def filter_recent_and_future_tournaments(tournaments: List[Dict]) -> List[Dict]:
    """Filter tournaments to include those held in the past six months and future tournaments."""
    current_date = date.today()
    six_months_ago = current_date - timedelta(days=6 * 30)
    relevant_tournaments = []

    for tournament in tournaments:
        start_date_str = tournament.get('start_date', '')

        if not start_date_str or start_date_str in ['N/A', 'TBD', 'To be announced']:
            relevant_tournaments.append(tournament)
            continue

        try:
            tournament_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if six_months_ago <= tournament_start_date:
                relevant_tournaments.append(tournament)
        except ValueError:
            continue

    return relevant_tournaments


@app.route('/')
def api_docs():
    """API documentation endpoint."""
    return {
        "message": "🏆 Tournament Calendar API",
        "version": "1.0.0",
        "endpoints": {
            "/search": "GET - Search tournaments by sport and level",
            "/health": "GET - Health check",
            "/": "GET - This documentation"
        },
        "usage": {
            "search": "/search?sport=Cricket&level=International",
            "supported_sports": [
                "Cricket", "Football", "Basketball", "Tennis", 
                "Badminton", "Swimming", "Running", "Cycling", 
                "Chess", "Table Tennis", "Kabaddi", "Yoga", "Gym"
            ],
            "supported_levels": ["International"]
        },
        "status": "🚀 API Ready"
    }


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "query_generator": query_generator is not None,
            "search_collector": search_collector is not None,
            "content_extractor": content_extractor is not None,
            "data_processor": data_processor is not None
        }
    }


@app.route('/search')
def search_tournaments():
    """
    Search tournaments by sport and level.
    
    Query Parameters:
    - sport: The sport to search for (required)
    - level: Tournament level (required, currently only 'International' supported)
    
    Returns:
    - JSON response with tournament results
    """
    try:
        # Get query parameters
        sport = request.args.get('sport', '').strip()
        level = request.args.get('level', '').strip()
        
        # Validate parameters
        if not sport:
            return jsonify({
                "error": "Missing required parameter: sport",
                "message": "Please provide a sport parameter"
            }), 400
        
        if not level:
            return jsonify({
                "error": "Missing required parameter: level", 
                "message": "Please provide a level parameter"
            }), 400
        
        if level != "International":
            return jsonify({
                "error": "Invalid level",
                "message": "Currently only 'International' level is supported"
            }), 400
        
        print(f"🔍 API Request: Searching for {sport} tournaments at {level} level...")
        
        # Step 1: Generate sport-specific queries
        print("   📋 Generating sport-specific queries...")
        all_queries = query_generator.generate_all_queries(use_llm_enhancement=False)
        
        # Filter queries by sport
        sport_queries = [q for q in all_queries if q.get('sport', '').lower() == sport.lower()]
        
        if not sport_queries:
            return jsonify({
                "error": "Sport not supported",
                "message": f"No queries available for sport: {sport}",
                "supported_sports": [
                    "Cricket", "Football", "Basketball", "Tennis", 
                    "Badminton", "Swimming", "Running", "Cycling", 
                    "Chess", "Table Tennis", "Kabaddi", "Yoga", "Gym"
                ]
            }), 400
        
        # Use 8 queries with 8 results each for 32 total results
        sport_queries = sport_queries[:8]  # Use 8 queries for 32 total results (8x8)
        print(f"   ✅ Using {len(sport_queries)} {sport} queries")
        
        # Step 2: Collect search results
        print("   🌐 Collecting search results...")
        all_search_results = []
        
        for i, query_data in enumerate(sport_queries, 1):
            query_text = query_data.get('query', str(query_data))
            print(f"      Query {i}/{len(sport_queries)}: {query_text[:50]}...")
            
            results = search_collector.search_query(query_text, num_results=8)
            if results and 'organic' in results:
                organic_results = results['organic']
                all_search_results.extend(organic_results)
        
        print(f"   ✅ Collected {len(all_search_results)} search results")
        
        if not all_search_results:
            return jsonify({
                "sport": sport,
                "level": level,
                "tournaments": [],
                "message": "No search results found for this sport",
                "query_count": len(sport_queries)
            })
        
        # Step 3: Extract tournament data
        print("   🎯 Extracting tournament data...")
        tournaments = content_extractor.extract_tournaments_batch(
            search_results=all_search_results,
            max_urls=None,  # Process all available URLs (like original system)
            use_structured=True
        )
        
        if not tournaments:
            return jsonify({
                "sport": sport,
                "level": level,
                "tournaments": [],
                "message": "No tournaments could be extracted from search results",
                "search_results_count": len(all_search_results)
            })
        
        # Step 4: Process and deduplicate
        print("   🔄 Processing tournament data...")
        unique_tournaments = data_processor.deduplicate_tournaments(tournaments)
        
        # Step 5: Filter for recent and future tournaments
        relevant_tournaments = filter_recent_and_future_tournaments(unique_tournaments)
        
        print(f"   ✅ Found {len(relevant_tournaments)} relevant tournaments")
        
        # Return results
        return jsonify({
            "sport": sport,
            "level": level,
            "tournaments": relevant_tournaments,
            "metadata": {
                "total_found": len(relevant_tournaments),
                "queries_used": len(sport_queries),
                "search_results": len(all_search_results),
                "extraction_method": "schema-based",
                "timestamp": datetime.now().isoformat()
            },
            "message": f"Successfully found {len(relevant_tournaments)} {sport} tournaments"
        })
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "sport": request.args.get('sport', 'unknown'),
            "level": request.args.get('level', 'unknown')
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Available endpoints: /, /health, /search",
        "usage": "/search?sport=Cricket&level=International"
    }), 404


def main():
    """Main function to start the API server."""
    print("🏆 Tournament Calendar API Server")
    print("=" * 50)
    
    # Initialize services
    if not initialize_services():
        print("❌ Failed to initialize services. Please check your .env file.")
        return 1
    
    print("\n🔧 Configuration:")
    print("   • Port: 8000")
    print("   • Host: localhost")
    print("   • CORS: Enabled")
    print("   • Debug: True")
    
    print(f"\n🚀 Starting API server...")
    print(f"   • API Documentation: http://localhost:8000/")
    print(f"   • Health Check: http://localhost:8000/health")
    print(f"   • Search Endpoint: http://localhost:8000/search?sport=Cricket&level=International")
    print(f"\n📱 Your frontend can now connect to: http://localhost:8000/search")
    
    try:
        # Start the Flask development server
        app.run(
            host='localhost',
            port=8000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid double initialization
        )
    except KeyboardInterrupt:
        print("\n⚠️  Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
