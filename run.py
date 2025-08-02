#!/usr/bin/env python3
"""
Tournament System - Main Entry Point

Unified entry point for tournament data processing.
"""

import sys
import argparse
import subprocess
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tournament_system.api import create_app
from tournament_system.core.query_generator import QueryGenerator
from tournament_system.core.search_collector import SearchResultsCollector
from tournament_system.core.content_extractor import ContentExtractor
from tournament_system.core.data_processor import TournamentDataProcessor
from tournament_system.exporters.data_exporter import TournamentDataExporter


def run_server(port=5000, debug=True):
    """Run the API server."""
    print("🚀 Starting Tournament System API Server")
    print("=" * 50)
    print(f"📡 Server: http://localhost:{port}")
    print(f"📊 Health: http://localhost:{port}/health")
    print(f"🔧 API Docs: http://localhost:{port}/docs")
    print("=" * 50)
    
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=debug)


def run_dev_mode():
    """Run both frontend and backend in development mode."""
    import subprocess
    import time
    from pathlib import Path
    
    print("🚀 Starting Tournament System - Development Mode")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🚀 Backend:  http://localhost:8000")
    print("📊 Health:   http://localhost:8000/health")
    print("=" * 50)
    
    try:
        print("\n🖥️ Starting Backend API Server (Port 8000)...")
        backend = subprocess.Popen([
            sys.executable, "run.py", "server", "--port", "8000"
        ])
        
        print("⏳ Waiting for backend to initialize...")
        time.sleep(3)
        
        print("\n🌐 Starting Frontend Server (Port 3000)...")
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            print("❌ Frontend directory not found")
            backend.terminate()
            return
            
        frontend = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=frontend_path)
        
        print("\n✅ Both services are running!")
        print("💡 Press Ctrl+C to stop both services")
        
        # Wait for user interruption
        try:
            while True:
                time.sleep(1)
                if backend.poll() is not None or frontend.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend.terminate()
            frontend.terminate()
            print("✅ Services stopped.")
            
    except Exception as e:
        print(f"❌ Error in dev mode: {e}")


def run_batch_processing(sport: str = "Cricket", max_tournaments: int = None):
    """Run batch processing pipeline."""
    print("🔄 Starting Tournament System Batch Processing")
    print("=" * 60)
    print(f"🏆 Sport: {sport}")
    if max_tournaments:
        print(f"🔢 Max tournaments: {max_tournaments}")
    print("=" * 60)
    
    # Step 1: Generate queries
    print("\n1️⃣ Generating search queries...")
    generator = QueryGenerator()
    queries = generator.generate_all_queries()
    print(f"✅ Generated {len(queries)} queries")
    
    # Step 2: Collect search results
    print("\n2️⃣ Collecting search results...")
    collector = SearchResultsCollector()
    search_results = collector.collect_all_search_results(queries)
    print(f"✅ Collected {len(search_results)} search results")
    
    # Step 3: Extract content
    print("\n3️⃣ Extracting tournament content...")
    extractor = ContentExtractor()
    tournaments = extractor.extract_tournaments_batch(
        search_results, 
        max_urls=max_tournaments,
        use_structured=True
    )
    print(f"✅ Extracted {len(tournaments)} tournaments")
    
    # Step 4: Process and deduplicate
    print("\n4️⃣ Processing tournament data...")
    processor = TournamentDataProcessor()
    processed_tournaments = processor.deduplicate_tournaments(tournaments)
    print(f"✅ Processed {len(processed_tournaments)} unique tournaments")
    
    # Step 5: Export data
    print("\n5️⃣ Exporting tournament data...")
    exporter = TournamentDataExporter()
    export_info = exporter.export_tournaments(processed_tournaments, sport)
    print(f"✅ Exported to: {export_info.get('csv_file', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("🎉 Batch processing completed successfully!")
    print(f"📊 Total tournaments: {len(processed_tournaments)}")
    print(f"📁 Files exported: CSV, JSON")
    print("=" * 60)
    
    return processed_tournaments


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tournament System - Essential Tournament Data Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py server                    # Run API server
  python run.py server --port 8000       # Run API server on port 8000
  python run.py batch                     # Run batch processing
  python run.py batch --sport Cricket    # Process Cricket tournaments
  python run.py batch --max 50           # Limit to 50 tournaments
  python run.py dev                       # Start both frontend and backend
        """
    )
    
    parser.add_argument(
        'mode', 
        choices=['server', 'batch', 'dev'],
        help='Operation mode: server (API), batch (processing), or dev (both services)'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Port for API server (default: 5000)'
    )
    
    parser.add_argument(
        '--sport', 
        default='Cricket',
        help='Sport to process (default: Cricket)'
    )
    
    parser.add_argument(
        '--max', 
        type=int,
        help='Maximum tournaments to process'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'server':
            run_server(port=args.port, debug=args.debug)
        elif args.mode == 'batch':
            run_batch_processing(sport=args.sport, max_tournaments=args.max)
        elif args.mode == 'dev':
            run_dev_mode()
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
