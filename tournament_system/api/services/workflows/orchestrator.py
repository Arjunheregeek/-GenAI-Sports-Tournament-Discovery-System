#!/usr/bin/env python3
"""
Workflow Orchestrator Module

Clean orchestrator that coordinates workflow execution.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from ...models import TournamentMetadata, ExportInfo, ProcessingSummary
    from ..processing_engine import TournamentProcessingEngine
    from ..tournament_filter import TournamentFilterService
    from ..export_manager import ExportManagerService
    from .executor import WorkflowExecutor
except ImportError:
    from tournament_system.api.models import TournamentMetadata, ExportInfo, ProcessingSummary
    from tournament_system.api.services.processing_engine import TournamentProcessingEngine
    from tournament_system.api.services.tournament_filter import TournamentFilterService
    from tournament_system.api.services.export_manager import ExportManagerService
    from tournament_system.api.services.workflows.executor import WorkflowExecutor


class WorkflowOrchestrator:
    """Clean orchestrator for tournament processing workflows."""
    
    def __init__(self):
        """Initialize workflow components."""
        self.processing_engine = TournamentProcessingEngine()
        self.filter_service = TournamentFilterService()
        self.export_manager = ExportManagerService()
        self.executor = WorkflowExecutor()
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize all components."""
        try:
            if not self.processing_engine.initialize_components() or not self.export_manager.initialize():
                raise Exception("Component initialization failed")
            self.initialized = True
            print("✅ Workflow orchestrator initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Workflow orchestrator error: {e}")
            return False
    
    def execute_comprehensive_workflow(self, sport: str, export_files: bool = True) -> Tuple[List[Dict], TournamentMetadata, ExportInfo, ProcessingSummary]:
        """Execute comprehensive workflow."""
        if not self.initialized:
            raise Exception("Orchestrator not initialized")
        return self.executor.execute_comprehensive(self.processing_engine, self.filter_service, self.export_manager, sport, export_files)
    
    def execute_quick_workflow(self, sport: str, level: str = "International", export_files: bool = False) -> Tuple[List[Dict], TournamentMetadata, ExportInfo]:
        """Execute quick workflow."""
        if not self.initialized:
            raise Exception("Orchestrator not initialized")
        return self.executor.execute_quick(self.processing_engine, self.filter_service, self.export_manager, sport, level, export_files)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        processing_status = self.processing_engine.get_component_status()
        return {
            "workflow_initialized": self.initialized,
            "export_manager_initialized": self.export_manager.is_initialized(),
            "processing_components": processing_status,
            "all_systems_ready": self.initialized and self.export_manager.is_initialized() and all(processing_status.values())
        }
