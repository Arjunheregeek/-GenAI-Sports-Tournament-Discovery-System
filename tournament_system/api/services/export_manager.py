#!/usr/bin/env python3
"""
Export Manager Service

Handles file exports and data persistence.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Add project root to path for tournament_system imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Tournament system imports
from tournament_system.exporters.data_exporter import TournamentDataExporter

# Use relative import for api models
try:
    from ..models import ExportInfo
except ImportError:
    # Fallback for when module is run directly
    sys.path.insert(0, str(project_root))
    from tournament_system.api.models import ExportInfo


class ExportManagerService:
    """Service for managing tournament data exports."""
    
    def __init__(self):
        """Initialize export manager."""
        self.data_exporter: Optional[TournamentDataExporter] = None
    
    def initialize(self) -> bool:
        """Initialize data exporter."""
        try:
            self.data_exporter = TournamentDataExporter()
            return True
        except Exception as e:
            print(f"❌ Export manager initialization error: {e}")
            return False
    
    def export_tournaments(
        self, 
        tournaments: List[Dict], 
        filename_prefix: str,
        export_enabled: bool = True
    ) -> ExportInfo:
        """
        Export tournaments to CSV and JSON files.
        
        Args:
            tournaments: List of tournament dictionaries
            filename_prefix: Prefix for output files
            export_enabled: Whether to actually perform export
            
        Returns:
            ExportInfo object with export results
        """
        if not export_enabled or not tournaments:
            return ExportInfo(status="skipped")
        
        if not self.data_exporter:
            return ExportInfo(status="failed", error="Data exporter not initialized")
        
        try:
            print("💾 Exporting tournament data...")
            csv_file, json_file = self.data_exporter.export_tournaments(
                tournaments, 
                filename_prefix
            )
            
            export_info = ExportInfo(
                status="success",
                csv_file=csv_file,
                json_file=json_file,
                export_timestamp=datetime.now().isoformat()
            )
            
            print(f"✅ Export completed: {csv_file}, {json_file}")
            return export_info
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return ExportInfo(status="failed", error=str(e))
    
    def get_export_statistics(self, tournaments: List[Dict]) -> Dict[str, Any]:
        """
        Generate export statistics for tournaments.
        
        Args:
            tournaments: List of tournament dictionaries
            
        Returns:
            Dictionary with export statistics
        """
        if not tournaments:
            return {
                "total_tournaments": 0,
                "tournaments_with_dates": 0,
                "tournaments_with_venues": 0,
                "tournaments_with_urls": 0
            }
        
        stats = {
            "total_tournaments": len(tournaments),
            "tournaments_with_dates": sum(1 for t in tournaments if t.get('start_date') and t['start_date'] not in ['N/A', 'TBD']),
            "tournaments_with_venues": sum(1 for t in tournaments if t.get('venue') and t['venue'].strip()),
            "tournaments_with_urls": sum(1 for t in tournaments if t.get('tournament_url') and t['tournament_url'].strip()),
            "tournaments_with_streaming": sum(1 for t in tournaments if t.get('streaming_links')),
            "tournaments_with_images": sum(1 for t in tournaments if t.get('images'))
        }
        
        return stats
    
    def is_initialized(self) -> bool:
        """Check if export manager is initialized."""
        return self.data_exporter is not None
