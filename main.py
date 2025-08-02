#!/usr/bin/env python3
"""
Tournament Calendar Main Application

This is the main entry point for the Tournament Calendar application.
It uses the professional modular structure to extract tournament information
from various sports websites and export it in multiple formats.

Usage:
    python main.py

Requirements:
    - All API keys configured in .env file
    - Required packages installed (pip install -r requirements.txt)
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tournament_calendar.core.config import APIConfig, validate_config
from tournament_calendar.core.data_processor import TournamentDataProcessor


def main():
    """Main application entry point."""
    
    print("🏆 Tournament Calendar Application")
    print("=" * 50)
    
    # Step 1: Validate configuration
    print("🔧 Step 1: Validating configuration...")
    try:
        validate_config()
        print("✅ Configuration validated successfully!")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Please check your .env file and ensure all required API keys are set.")
        return 1
    
    # Step 2: Initialize the data processor
    print("\n🚀 Step 2: Initializing Tournament Data Processor...")
    try:
        processor = TournamentDataProcessor()
        print("✅ Data processor initialized successfully!")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return 1
    
    # Step 3: Process tournaments
    print("\n📊 Step 3: Processing tournament data...")
    try:
        # Define search queries for cricket tournaments
        search_queries = [
            "cricket tournament schedule 2025 international matches",
            "ICC cricket world cup 2025 fixtures dates",
            "T20 cricket series 2025 calendar schedule",
            "Test cricket matches 2025 international tours",
            "ODI cricket tournaments 2025 upcoming series"
        ]
        
        # Process the tournaments
        results = processor.process_tournaments(search_queries)
        
        if results and len(results) > 0:
            print(f"✅ Successfully processed {len(results)} tournaments!")
            
            # Display summary
            print(f"\n📋 Tournament Summary:")
            for i, tournament in enumerate(results[:5], 1):  # Show first 5
                print(f"   {i}. {tournament.get('tournament_name', 'N/A')}")
                print(f"      📅 {tournament.get('start_date', 'N/A')} - {tournament.get('end_date', 'N/A')}")
                print(f"      🏟️  {tournament.get('venue', 'N/A')}")
                print()
            
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more tournaments")
            
        else:
            print("⚠️  No tournaments were processed successfully.")
            return 1
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return 1
    
    # Step 4: Export results
    print("\n📄 Step 4: Exporting results...")
    try:
        # Export to different formats
        export_success = processor.export_results(results)
        
        if export_success:
            print("✅ Results exported successfully!")
            print("📁 Check the output directory for exported files:")
            print("   • CSV format: tournaments.csv")
            print("   • JSON format: tournaments.json")
        else:
            print("⚠️  Export completed with some issues. Check the logs above.")
            
    except Exception as e:
        print(f"❌ Export error: {e}")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 Tournament Calendar processing completed successfully!")
    print("📊 Summary:")
    print(f"   • Tournaments processed: {len(results) if results else 0}")
    print(f"   • Export formats: CSV, JSON")
    print(f"   • Configuration: ✅ Valid")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
