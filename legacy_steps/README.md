# Legacy Step Files

This folder contains the original step-by-step implementation files that were used during development but are now replaced by the professional modular structure in the `tournament_calendar/` package.

## Files in this folder:

### Original Step Files:
- `step1_generate_queries.py` - Original query generation logic
- `step2_search_results.py` - Original search results collection
- `step3_extract_content.py` - Original content extraction
- `step4_process_tournaments.py` - Original tournament processing
- `step5_database_operations.py` - Original database operations
- `step6_final_export.py` - Original export functionality

### Legacy Support Files:
- `config.py` - Original configuration file (replaced by `tournament_calendar/core/config.py`)
- `collect_search_results.py` - Legacy search collection script
- `export_tournaments.py` - Legacy export script
- `generate_queries.py` - Legacy query generation script
- `mysql_integration.py` - Legacy MySQL integration
- `test_firecrawl_key.py` - Test helper file

## Note:
These files are kept for reference and historical purposes. The active codebase now uses the professional modular structure in:
- `tournament_calendar/` - Main package
- `tests/` - Test files
- `main.py` - Main entry point

**DO NOT USE THESE FILES** - They may have import conflicts and outdated dependencies. Use the main tournament_calendar package instead.
