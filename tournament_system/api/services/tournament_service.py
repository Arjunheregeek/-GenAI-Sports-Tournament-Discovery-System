#!/usr/bin/env python3
"""
Tournament Service Module

Clean service facade for tournament processing operations.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Tournament system imports
from tournament_system.core.config import validate_config

# Use relative imports for api modules
try:
    from ..models import TournamentMetadata, ExportInfo, ProcessingSummary
    from .workflows import WorkflowOrchestrator
except ImportError:
    # Fallback for when module is run directly
    from tournament_system.api.models import TournamentMetadata, ExportInfo, ProcessingSummary
    from tournament_system.api.services.workflows import WorkflowOrchestrator


class TournamentService:
    """
    Clean service facade for tournament processing operations.
    
    This service provides a simple interface to tournament processing workflows
    while maintaining backward compatibility with the original API.
    """
    
    def __init__(self):
        """Initialize tournament service."""
        self.orchestrator = WorkflowOrchestrator()
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize tournament service and all underlying components."""
        try:
            # Validate configuration first
            config_errors = validate_config()
            if config_errors:
                raise Exception(f"Configuration validation failed: {', '.join(config_errors)}")
            
            # Initialize workflow orchestrator
            if not self.orchestrator.initialize():
                raise Exception("Orchestrator initialization failed")
            
            self.initialized = True
            print("✅ Tournament service initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Tournament service initialization error: {e}")
            self.initialized = False
            return False
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get the status of all services."""
        if not self.initialized:
            return {"tournament_service": False, "orchestrator": False, "initialized": False}
        
        system_status = self.orchestrator.get_system_status()
        return {
            "tournament_service": self.initialized,
            "orchestrator": system_status.get("workflow_initialized", False),
            "all_systems_ready": system_status.get("all_systems_ready", False),
            "initialized": self.initialized and system_status.get("all_systems_ready", False)
        }
    
    def process_comprehensive_tournaments(
        self, 
        sport: str, 
        export_files: bool = True
    ) -> Tuple[List[Dict], TournamentMetadata, ExportInfo, ProcessingSummary]:
        """Execute comprehensive tournament processing workflow."""
        if not self.initialized:
            raise Exception("Tournament service not initialized")
        return self.orchestrator.execute_comprehensive_workflow(sport, export_files)
    
    def process_quick_search(
        self, 
        sport: str, 
        level: str = "International", 
        export_files: bool = False
    ) -> Tuple[List[Dict], TournamentMetadata, ExportInfo]:
        """Execute quick tournament search workflow."""
        if not self.initialized:
            raise Exception("Tournament service not initialized")
        return self.orchestrator.execute_quick_workflow(sport, level, export_files)
    
    # Backward compatibility method (legacy interface)
    def filter_recent_and_future_tournaments(self, tournaments: List[Dict]) -> List[Dict]:
        """Legacy method for backward compatibility."""
        try:
            from .tournament_filter import TournamentFilterService
        except ImportError:
            from tournament_system.api.services.tournament_filter import TournamentFilterService
        return TournamentFilterService.filter_recent_and_future_tournaments(tournaments)
