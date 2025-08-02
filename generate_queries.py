#!/usr/bin/env python3
"""
Query Generation Runner

This script maintains compatibility with the original step1_generate_queries.py
while using the new structured modules.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import from the new structure
from tournament_calendar.core.query_generator import main

if __name__ == "__main__":
    main()
