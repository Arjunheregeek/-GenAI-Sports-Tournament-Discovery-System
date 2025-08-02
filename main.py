#!/usr/bin/env python3
"""
Tournament Calendar Main Application

This is the main entry point for the Tournament Calendar application.
It orchestrates the complete workflow from query generation to final export.

Workflow:
1. Validate Configuration & API Keys
2. Generate Search Queries  
3. Collect Search Results
4. Extract Content from URLs
5. Process Tournaments with AI
6. Export Results to CSV/JSON

Usage:
    python main.py

Requirements:
    - All API keys configured in .env file
    - Required packages installed (pip install -r requirements.txt)
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime, date, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all required modules
from tournament_calendar.core.config import APIConfig, validate_config
from tournament_calendar.core.query_generator import QueryGenerator
from tournament_calendar.core.search_collector import SearchResultsCollector
from tournament_calendar.core.content_extractor import ContentExtractor
from tournament_calendar.core.data_processor import TournamentDataProcessor
from tournament_calendar.exporters.data_exporter import TournamentDataExporter


def filter_recent_and_future_tournaments(tournaments: List[Dict]) -> List[Dict]:
    """
    Filter tournaments to include those held in the past six months and future tournaments.

    Args:
        tournaments: List of tournament dictionaries

    Returns:
        List of tournaments within the past six months or in the future.
    """
    current_date = date.today()
    six_months_ago = current_date - timedelta(days=6 * 30)  # Approximation for six months
    relevant_tournaments = []

    print(f"   📅 Current date: {current_date}")
    print(f"   🔍 Filtering tournaments to include past six months and future events...")

    for tournament in tournaments:
        start_date_str = tournament.get('start_date', '')

        # Skip tournaments without start dates
        if not start_date_str or start_date_str in ['N/A', 'TBD', 'To be announced']:
            # Keep tournaments without specific dates (they might be relevant)
            relevant_tournaments.append(tournament)
            continue

        try:
            # Parse different date formats
            tournament_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

            # Check if the tournament is within the past six months or in the future
            if six_months_ago <= tournament_start_date:
                relevant_tournaments.append(tournament)
        except ValueError:
            print(f"⚠️ Unable to parse date for tournament: {tournament.get('tournament_name', 'Unknown')}")

    print(f"   ✅ Total relevant tournaments: {len(relevant_tournaments)}")
    return relevant_tournaments


def main():
    """Main application entry point orchestrating the complete tournament extraction workflow."""
    
    print("🏆 Tournament Calendar Application")
    print("=" * 60)
    print("🚀 Complete Tournament Data Extraction and Processing Pipeline")
    print("=" * 60)
    
    # Step 1: Validate Configuration
    print("\n🔧 STEP 1: Validating configuration and API keys...")
    try:
        validate_config()
        print("✅ All configurations validated successfully!")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Please check your .env file and ensure all required API keys are set:")
        print("   • SERPER_API_KEY - for search results")
        print("   • FIRECRAWL_API_KEY - for content extraction")
        print("   • OPENAI_API_KEY - for AI processing")
        return 1
    
    # Step 2: Generate Search Queries
    print("\n🔍 STEP 2: Generating comprehensive search queries...")
    try:
        query_generator = QueryGenerator()
        
        # Generate all queries (base + enhanced)
        print("   🎯 Generating complete cricket tournament query set...")
        all_queries = query_generator.generate_all_queries(use_llm_enhancement=False)  # Disable LLM for faster testing
        
        # Filter to cricket only and limit for demo
        cricket_queries = [q for q in all_queries if q.get('sport') == 'Cricket'][:15]
        
        print(f"✅ Generated {len(cricket_queries)} cricket tournament queries!")
        print("\n📋 Sample queries:")
        for i, query_data in enumerate(cricket_queries[:3], 1):
            query_text = query_data.get('query', str(query_data))
            print(f"   {i}. {query_text}")
        
    except Exception as e:
        print(f"❌ Query generation error: {e}")
        return 1
    
    # Step 3: Collect Search Results
    print("\n📊 STEP 3: Collecting search results from web...")
    try:
        search_collector = SearchResultsCollector()
        
        if not search_collector.validate_api_key():
            return 1
            
        print(f"   🔍 Processing {len(cricket_queries)} search queries...")
        all_search_results = []
        
        # Process queries in batches
        for i, query_data in enumerate(cricket_queries, 1):
            query_text = query_data.get('query', str(query_data))
            
            print(f"      Query {i}/{len(cricket_queries)}: {query_text[:60]}...")
            
            results = search_collector.search_query(query_text, num_results=8)
            if results and 'organic' in results:
                organic_results = results['organic']
                print(f"        ✅ Found {len(organic_results)} results")
                all_search_results.extend(organic_results)
            else:
                print(f"        ⚠️  No organic results found")
        
        print(f"✅ Collected {len(all_search_results)} total search results!")
        
    except Exception as e:
        print(f"❌ Search collection error: {e}")
        return 1
    
    # Step 4: Extract Content from URLs
    print("\n🌐 STEP 4: Extracting content from tournament websites...")
    try:
        content_extractor = ContentExtractor()
        
        if not content_extractor.validate_and_initialize():
            return 1
        
        # Extract unique URLs
        unique_urls = list(set([result.get('link') for result in all_search_results if result.get('link')]))
        
        # Limit URLs for demo (remove this limit for production)
        demo_urls = unique_urls[:10]
        print(f"   📝 Extracting content from {len(demo_urls)} unique URLs...")
        
        extracted_content = []
        successful_extractions = 0
        
        for i, url in enumerate(demo_urls, 1):
            print(f"      URL {i}/{len(demo_urls)}: {url[:50]}...")
            
            content = content_extractor.extract_single_url(url)
            if content and content.get('content'):
                extracted_content.append(content)
                word_count = content.get('word_count', 0)
                quality_score = content.get('quality_score', 0)
                print(f"        ✅ Extracted {word_count} words (Quality: {quality_score:.1f})")
                successful_extractions += 1
            else:
                print(f"        ❌ Failed to extract content")
        
        print(f"✅ Successfully extracted content from {successful_extractions}/{len(demo_urls)} URLs!")
        
        if not extracted_content:
            print("❌ No content was successfully extracted. Cannot proceed.")
            return 1
            
    except Exception as e:
        print(f"❌ Content extraction error: {e}")
        return 1
    
    # Step 5: Process Tournaments with AI
    print("\n🤖 STEP 5: Processing tournaments with AI (OpenAI GPT)...")
    try:
        data_processor = TournamentDataProcessor()
        
        if not data_processor.validate_api_key():
            return 1
        
        print(f"   🧠 Analyzing {len(extracted_content)} content items for tournament data...")
        
        # Process content with AI to extract structured tournament data
        tournaments = data_processor.process_all_content(
            extracted_content, 
            max_items=10  # Limit for demo
        )
        
        if tournaments and len(tournaments) > 0:
            # Deduplicate tournaments
            unique_tournaments = data_processor.deduplicate_tournaments(tournaments)
            
            print(f"✅ Successfully processed {len(tournaments)} tournaments!")
            print(f"🎯 Unique tournaments after deduplication: {len(unique_tournaments)}")
            
            # Display tournament summary
            print(f"\n📋 Tournament Summary (Top 5):")
            for i, tournament in enumerate(unique_tournaments[:5], 1):
                name = tournament.get('tournament_name', 'N/A')
                dates = f"{tournament.get('start_date', 'N/A')} - {tournament.get('end_date', 'N/A')}"
                venue = tournament.get('venue', 'N/A')
                level = tournament.get('level', 'N/A')
                
                print(f"   {i}. {name}")
                print(f"      📅 {dates}")
                print(f"      🏟️  {venue} ({level})")
                print()
            
            if len(unique_tournaments) > 5:
                print(f"   ... and {len(unique_tournaments) - 5} more tournaments")
                
            tournaments = unique_tournaments  # Use deduplicated tournaments
            
        else:
            print("❌ No tournaments were successfully processed.")
            return 1
            
    except Exception as e:
        print(f"❌ Tournament processing error: {e}")
        return 1
    
    # Step 5.5: Filter Recent and Future Tournaments Only
    print("\n📅 STEP 5.5: Filtering tournaments to include only past six months and future events...")
    try:
        recent_and_future_tournaments = filter_recent_and_future_tournaments(tournaments)
        
        if recent_and_future_tournaments and len(recent_and_future_tournaments) > 0:
            tournaments = recent_and_future_tournaments  # Update tournaments list
            print(f"✅ Tournament filtering completed! {len(tournaments)} relevant tournaments retained.")
            
            # Display filtered tournament summary
            print(f"\n📋 Relevant Tournament Summary (Top 5):")
            for i, tournament in enumerate(tournaments[:5], 1):
                name = tournament.get('tournament_name', 'N/A')
                dates = f"{tournament.get('start_date', 'N/A')} - {tournament.get('end_date', 'N/A')}"
                venue = tournament.get('venue', 'N/A')
                level = tournament.get('level', 'N/A')
                
                print(f"   {i}. {name}")
                print(f"      📅 {dates}")
                print(f"      🏟️  {venue} ({level})")
                print()
            
            if len(tournaments) > 5:
                print(f"   ... and {len(tournaments) - 5} more relevant tournaments")
        else:
            print("⚠️  No relevant tournaments found after filtering.")
            print("   This might be expected if no tournaments are within the desired date range.")
            # Continue with empty list for demonstration
            tournaments = []
            
    except Exception as e:
        print(f"❌ Tournament filtering error: {e}")
        # Continue with unfiltered tournaments if filtering fails
        pass
    
    # Step 6: Export Results
    print("\n📄 STEP 6: Exporting tournament data...")
    try:
        data_exporter = TournamentDataExporter(output_directory="final_output")
        
        print("   💾 Exporting to multiple formats...")
        
        # Export to CSV (assignment requirement)
        csv_file = data_exporter.export_to_csv(tournaments, "tournament_calendar_final.csv")
        
        # Export to JSON (backup format)
        json_file = data_exporter.export_to_json(tournaments, "tournament_calendar_final.json")
        
        # Generate export manifest
        try:
            manifest_file = data_exporter.export_manifest(tournaments, "export_manifest.json")
        except:
            manifest_file = None
        
        if csv_file and json_file:
            print("✅ All exports completed successfully!")
            print("\n📁 Generated Files:")
            print(f"   • CSV Format: {csv_file}")
            print(f"   • JSON Format: {json_file}")
            if manifest_file:
                print(f"   • Manifest: {manifest_file}")
        else:
            print("⚠️  Export completed with some issues.")
            
    except Exception as e:
        print(f"❌ Export error: {e}")
        return 1
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 TOURNAMENT CALENDAR PROCESSING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("📊 FINAL SUMMARY:")
    print(f"   • Search Queries Generated: {len(cricket_queries)}")
    print(f"   • Search Results Collected: {len(all_search_results)}")
    print(f"   • Content Items Extracted: {len(extracted_content)}")
    print(f"   • Tournaments Processed: {len(tournaments) if tournaments else 0}")
    print(f"   • Export Formats: CSV, JSON")
    print(f"   • Configuration Status: ✅ Valid")
    print("\n🎯 Ready for submission! Check the 'final_output' directory for results.")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user. Exiting gracefully...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error in main application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
