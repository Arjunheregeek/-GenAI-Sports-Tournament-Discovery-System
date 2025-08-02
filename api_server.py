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
from tournament_calendar.exporters.data_exporter import TournamentDataExporter

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global variables
query_generator = None
search_collector = None
content_extractor = None
data_processor = None
data_exporter = None


def initialize_services():
    """Initialize all tournament extraction services."""
    global query_generator, search_collector, content_extractor, data_processor, data_exporter
    
    try:
        # Validate configuration
        validate_config()
        
        # Initialize services (same as main.py)
        query_generator = QueryGenerator()
        search_collector = SearchResultsCollector()
        content_extractor = ContentExtractor()
        data_processor = TournamentDataProcessor()
        data_exporter = TournamentDataExporter()
        
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
        "message": "🏆 Tournament Calendar API - Comprehensive Edition",
        "version": "2.0.0",
        "description": "Merged functionality from main.py and api_server.py for comprehensive frontend integration",
        "endpoints": {
            "/search": "GET - Quick tournament search by sport and level (optimized for speed)",
            "/comprehensive": "GET - Full main.py workflow with comprehensive processing and export",
            "/health": "GET - Health check",
            "/": "GET - This documentation"
        },
        "usage": {
            "quick_search": "/search?sport=Cricket&level=International",
            "comprehensive": "/comprehensive?sport=Cricket&export=true",
            "supported_sports": [
                "Cricket", "Football", "Basketball", "Tennis", 
                "Badminton", "Swimming", "Running", "Cycling", 
                "Chess", "Table Tennis", "Kabaddi", "Yoga", "Gym"
            ],
            "supported_levels": ["International"]
        },
        "features": {
            "quick_search": "Fast tournament search with essential results",
            "comprehensive": "Complete main.py functionality: all queries, all URLs, full processing pipeline, file exports",
            "export_formats": ["CSV", "JSON"],
            "processing_approach": "Schema-based extraction with Firecrawl API"
        },
        "status": "🚀 API Ready - Main.py Functionality Integrated"
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
            "data_processor": data_processor is not None,
            "data_exporter": data_exporter is not None
        }
    }


@app.route('/comprehensive')
def comprehensive_processing():
    """
    Comprehensive tournament processing endpoint - replicates main.py functionality.
    
    Query Parameters:
    - sport: The sport to search for (optional, defaults to 'Cricket')
    - export: Whether to export results to files (optional, defaults to 'true')
    
    Returns:
    - JSON response with comprehensive tournament results and file exports
    """
    try:
        # Get query parameters
        sport = request.args.get('sport', 'Cricket').strip()
        export_files = request.args.get('export', 'true').lower() == 'true'
        
        print(f"🚀 COMPREHENSIVE PROCESSING: {sport} tournaments (main.py approach)")
        print("=" * 70)
        
        # Step 1: Generate comprehensive queries (like main.py)
        print("📋 STEP 1: Generating comprehensive search queries...")
        all_queries = query_generator.generate_all_queries(use_llm_enhancement=False)
        sport_queries = [q for q in all_queries if q.get('sport', '').lower() == sport.lower()]
        
        if not sport_queries:
            return jsonify({
                "error": "Sport not supported for comprehensive processing",
                "message": f"No queries available for sport: {sport}",
                "supported_sports": ["Cricket", "Football", "Basketball", "Tennis", "Badminton", "Swimming", "Running", "Cycling", "Chess", "Table Tennis", "Kabaddi", "Yoga", "Gym"]
            }), 400
        
        print(f"✅ Generated {len(sport_queries)} {sport} tournament queries")
        
        # Step 2: Collect comprehensive search results (like main.py)
        print("📊 STEP 2: Collecting comprehensive search results...")
        all_search_results = []
        
        for i, query_data in enumerate(sport_queries, 1):
            query_text = query_data.get('query', str(query_data))
            print(f"   Query {i}/{len(sport_queries)}: {query_text[:60]}...")
            
            results = search_collector.search_query(query_text, num_results=8)
            if results and 'organic' in results:
                organic_results = results['organic']
                all_search_results.extend(organic_results)
                print(f"   ✅ Found {len(organic_results)} results")
            else:
                print(f"   ⚠️ No organic results found")
        
        print(f"✅ Collected {len(all_search_results)} total search results")
        
        # Step 3: Extract tournament data (comprehensive)
        print("🎯 STEP 3: Extracting tournament data...")
        tournaments = content_extractor.extract_tournaments_batch(
            search_results=all_search_results,
            max_urls=None,  # Process ALL URLs like main.py
            use_structured=True
        )
        
        print(f"✅ Extracted {len(tournaments) if tournaments else 0} tournaments")
        
        # Step 4: Process and deduplicate
        print("🔄 STEP 4: Processing and deduplicating tournaments...")
        if tournaments:
            unique_tournaments = data_processor.deduplicate_tournaments(tournaments)
            print(f"✅ {len(unique_tournaments)} unique tournaments after deduplication")
        else:
            unique_tournaments = []
        
        # Step 5: Filter recent and future tournaments
        print("📅 STEP 5: Filtering for recent and future tournaments...")
        relevant_tournaments = filter_recent_and_future_tournaments(unique_tournaments)
        print(f"✅ {len(relevant_tournaments)} relevant tournaments retained")
        
        # Step 6: Export results (like main.py)
        export_info = {}
        if export_files and relevant_tournaments:
            print("💾 STEP 6: Exporting comprehensive results...")
            try:
                csv_file, json_file, manifest_file = data_exporter.export_tournaments(
                    relevant_tournaments,
                    formats=['csv', 'json'],
                    filename_prefix=f"{sport.lower()}_comprehensive"
                )
                
                export_info = {
                    "csv_file": csv_file,
                    "json_file": json_file,
                    "manifest_file": manifest_file,
                    "export_timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
                print(f"✅ Export completed: {csv_file}, {json_file}")
                
            except Exception as e:
                export_info = {"status": "failed", "error": str(e)}
                print(f"❌ Export failed: {e}")
        
        # Final summary (like main.py)
        print("\n🎉 COMPREHENSIVE PROCESSING COMPLETED!")
        print(f"📊 Summary: {len(sport_queries)} queries → {len(all_search_results)} results → {len(relevant_tournaments)} tournaments")
        
        return jsonify({
            "status": "success",
            "sport": sport,
            "processing_type": "comprehensive_main_py_approach",
            "tournaments": relevant_tournaments,
            "summary": {
                "queries_generated": len(sport_queries),
                "search_results_collected": len(all_search_results),
                "tournaments_extracted": len(tournaments) if tournaments else 0,
                "unique_tournaments": len(unique_tournaments),
                "relevant_tournaments": len(relevant_tournaments),
                "processing_pipeline": "Generate→Search→Extract→Deduplicate→Filter→Export"
            },
            "export_info": export_info,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "extraction_method": "comprehensive_schema_based",
                "url_processing": "all_available_urls",
                "approach": "replicated_main_py_functionality"
            },
            "message": f"Comprehensive processing completed: {len(relevant_tournaments)} {sport} tournaments found and processed"
        })
        
    except Exception as e:
        print(f"❌ Comprehensive processing error: {e}")
        return jsonify({
            "status": "error",
            "error": "Comprehensive processing failed",
            "message": str(e),
            "sport": request.args.get('sport', 'Cricket')
        }), 500


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
        
        # Use comprehensive query approach (like main.py) - all available queries for thorough coverage
        # Filter to sport-specific queries and use all of them for maximum coverage
        print(f"   ✅ Using {len(sport_queries)} {sport} queries (comprehensive coverage like main.py)")
        
        # Step 2: Collect search results
        print("   🌐 Collecting search results...")
        all_search_results = []
        
        for i, query_data in enumerate(sport_queries, 1):
            query_text = query_data.get('query', str(query_data))
            print(f"      Query {i}/{len(sport_queries)}: {query_text[:50]}...")
            
            results = search_collector.search_query(query_text, num_results=8)  # 8 results per query like main.py
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
        
        # Step 6: Optional export (like main.py) - save to files for comprehensive datasets
        export_data = None
        if len(relevant_tournaments) > 0:
            try:
                print("   💾 Exporting results to files...")
                # Export to both CSV and JSON (like main.py)
                csv_file, json_file, manifest_file = data_exporter.export_tournaments(
                    relevant_tournaments,
                    formats=['csv', 'json'],
                    filename_prefix=f"{sport.lower()}_tournaments_api"
                )
                
                export_data = {
                    "csv_file": csv_file,
                    "json_file": json_file,
                    "manifest_file": manifest_file,
                    "export_timestamp": datetime.now().isoformat()
                }
                print(f"   ✅ Export completed: {csv_file}, {json_file}")
                
            except Exception as e:
                print(f"   ⚠️ Export failed: {e}")
                export_data = {"error": str(e)}
        
        # Return results (enhanced with main.py features)
        return jsonify({
            "sport": sport,
            "level": level,
            "tournaments": relevant_tournaments,
            "metadata": {
                "total_found": len(relevant_tournaments),
                "queries_used": len(sport_queries),
                "search_results": len(all_search_results),
                "extraction_method": "schema-based",
                "processing_approach": "comprehensive_like_main_py",
                "timestamp": datetime.now().isoformat(),
                "export_data": export_data
            },
            "message": f"Successfully found {len(relevant_tournaments)} {sport} tournaments",
            "summary": {
                "total_queries_processed": len(sport_queries),
                "total_search_results": len(all_search_results),
                "tournaments_extracted": len(relevant_tournaments),
                "processing_pipeline": "Query→Search→Extract→Process→Filter→Export"
            }
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
        "message": "Available endpoints: /, /health, /search, /comprehensive",
        "usage": {
            "quick_search": "/search?sport=Cricket&level=International",
            "comprehensive": "/comprehensive?sport=Cricket&export=true"
        }
    }), 404


def main():
    """Main function to start the comprehensive API server."""
    print("🏆 Tournament Calendar API Server - Comprehensive Edition")
    print("=" * 60)
    print("📋 Merged functionality from main.py for complete frontend integration")
    
    # Initialize services
    if not initialize_services():
        print("❌ Failed to initialize services. Please check your .env file.")
        return 1
    
    print("\n🔧 Configuration:")
    print("   • Port: 8000")
    print("   • Host: localhost")
    print("   • CORS: Enabled")
    print("   • Debug: True")
    print("   • Features: Quick search + Comprehensive processing")
    
    print(f"\n🚀 Starting comprehensive API server...")
    print(f"   • API Documentation: http://localhost:8000/")
    print(f"   • Health Check: http://localhost:8000/health")
    print(f"   • Quick Search: http://localhost:8000/search?sport=Cricket&level=International")
    print(f"   • Comprehensive: http://localhost:8000/comprehensive?sport=Cricket&export=true")
    print(f"\n📱 Your frontend now has access to full main.py functionality!")
    
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
