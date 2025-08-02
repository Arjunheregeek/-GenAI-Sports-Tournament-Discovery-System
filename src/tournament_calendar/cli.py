"""
Command Line Interface for Tournament Calendar System

Provides easy command-line access to all pipeline functionality.
"""

import argparse
import sys
import json
from typing import Optional, List

from ..core.pipeline import TournamentPipeline
from ..core.config import config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GenAI Tournament Calendar Data Collection System"
    )
    
    # Pipeline commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Full pipeline command
    pipeline_parser = subparsers.add_parser('run', help='Run the full pipeline')
    pipeline_parser.add_argument(
        '--skip-steps', 
        nargs='+', 
        type=int, 
        choices=range(1, 7),
        help='Steps to skip (1-6)'
    )
    
    # Single step command
    step_parser = subparsers.add_parser('step', help='Run a single step')
    step_parser.add_argument(
        'step_number', 
        type=int, 
        choices=range(1, 7),
        help='Step number to run (1-6)'
    )
    
    # Configuration commands
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument(
        '--validate', 
        action='store_true',
        help='Validate configuration'
    )
    config_parser.add_argument(
        '--show', 
        action='store_true',
        help='Show current configuration'
    )
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands
    if args.command == 'run':
        run_pipeline(args.skip_steps or [])
    elif args.command == 'step':
        run_single_step(args.step_number)
    elif args.command == 'config':
        handle_config_command(args)
    elif args.command == 'status':
        show_status()
    elif args.command == 'version':
        show_version()


def run_pipeline(skip_steps: List[int]):
    """Run the full pipeline."""
    print("🚀 Starting Tournament Calendar Pipeline")
    print("=" * 60)
    
    pipeline = TournamentPipeline()
    summary = pipeline.run_full_pipeline(skip_steps=skip_steps)
    
    print("\n" + "=" * 60)
    print("📊 Pipeline Execution Summary")
    print("=" * 60)
    print(f"Steps completed: {summary['steps_completed']}/{summary['total_steps']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    if summary['execution_time']:
        print(f"Execution time: {summary['execution_time']}")
    
    if summary['errors']:
        print(f"\n❌ Errors encountered:")
        for error in summary['errors']:
            print(f"   - {error}")
    else:
        print("\n✅ Pipeline completed successfully!")
    
    # Show step status
    print(f"\n📋 Step Status:")
    step_names = {
        'step_1_query_generation': 'Query Generation',
        'step_2_search_collection': 'Search Collection',
        'step_3_content_extraction': 'Content Extraction',
        'step_4_data_processing': 'Data Processing',
        'step_5_database_operations': 'Database Operations',
        'step_6_export_api': 'Export & API'
    }
    
    for step_key, step_name in step_names.items():
        status = "✅" if summary['step_status'][step_key] else "❌"
        print(f"   {status} {step_name}")


def run_single_step(step_number: int):
    """Run a single pipeline step."""
    step_names = {
        1: "Query Generation",
        2: "Search Collection", 
        3: "Content Extraction",
        4: "Data Processing",
        5: "Database Operations",
        6: "Export & API"
    }
    
    print(f"🚀 Running Step {step_number}: {step_names[step_number]}")
    print("=" * 60)
    
    pipeline = TournamentPipeline()
    success = pipeline.run_single_step(step_number)
    
    if success:
        print(f"✅ Step {step_number} completed successfully!")
    else:
        print(f"❌ Step {step_number} failed!")
        sys.exit(1)


def handle_config_command(args):
    """Handle configuration commands."""
    if args.validate:
        print("🔍 Validating configuration...")
        errors = config.validate_config()
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
        else:
            print("✅ Configuration validation passed!")
    
    elif args.show:
        print("📋 Current Configuration:")
        print("=" * 40)
        
        print(f"Sports ({len(config.SPORTS_LIST)}):")
        for i, sport in enumerate(config.SPORTS_LIST, 1):
            print(f"  {i}. {sport}")
        
        print(f"\nLevels ({len(config.LEVELS_LIST)}):")
        for i, level in enumerate(config.LEVELS_LIST, 1):
            print(f"  {i}. {level}")
        
        print(f"\nOutput Fields ({len(config.OUTPUT_FIELDS)}):")
        for field in config.OUTPUT_FIELDS:
            print(f"  - {field}")
        
        print(f"\nDatabase: {config.database_config.database}")
        print(f"Host: {config.database_config.host}:{config.database_config.port}")


def show_status():
    """Show system status."""
    print("📊 Tournament Calendar System Status")
    print("=" * 40)
    
    # Check API keys
    api_status = {
        'Serper API': bool(config.api_config.serper_api_key),
        'Firecrawl API': bool(config.api_config.firecrawl_api_key),
        'OpenAI API': bool(config.api_config.openai_api_key)
    }
    
    print("🔑 API Keys:")
    for api_name, configured in api_status.items():
        status = "✅" if configured else "❌"
        print(f"   {status} {api_name}")
    
    # Check database connection
    print(f"\n🗄️  Database:")
    print(f"   Host: {config.database_config.host}:{config.database_config.port}")
    print(f"   Database: {config.database_config.database}")
    print(f"   User: {config.database_config.user}")
    
    # Show coverage
    print(f"\n🎯 Coverage:")
    print(f"   Sports: {len(config.SPORTS_LIST)} configured")
    print(f"   Levels: {len(config.LEVELS_LIST)} configured")
    print(f"   Total combinations: {len(config.SPORTS_LIST) * len(config.LEVELS_LIST)}")


def show_version():
    """Show version information."""
    print("Tournament Calendar System")
    print("Version: 1.0.0")
    print("Author: GenAI Tournament Calendar Team")
    print("License: MIT")


if __name__ == '__main__':
    main()
