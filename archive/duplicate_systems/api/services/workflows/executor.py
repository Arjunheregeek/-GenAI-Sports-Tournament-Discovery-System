#!/usr/bin/env python3
"""
Workflow Executor Module

Executes complete tournament processing workflows using workflow steps.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from ...models import TournamentMetadata, ExportInfo, ProcessingSummary
    from .steps import WorkflowSteps
except ImportError:
    from api.models import TournamentMetadata, ExportInfo, ProcessingSummary
    from api.services.workflows.steps import WorkflowSteps


class WorkflowExecutor:
    """Executes tournament processing workflows by coordinating workflow steps."""
    
    def execute_comprehensive(self, processing_engine, filter_service, export_manager, sport: str, export_files: bool = True) -> Tuple[List[Dict], TournamentMetadata, ExportInfo, ProcessingSummary]:
        """Execute comprehensive tournament workflow."""
        start_time = datetime.now()
        
        print(f"🚀 COMPREHENSIVE WORKFLOW: {sport}")
        print("=" * 50)
        
        # Execute workflow steps
        queries = WorkflowSteps.generate_queries(processing_engine, sport)
        search_results = WorkflowSteps.collect_results(processing_engine, queries)
        tournaments = WorkflowSteps.extract_tournaments(processing_engine, search_results)
        unique_tournaments = WorkflowSteps.process_tournaments(processing_engine, tournaments)
        final_tournaments = WorkflowSteps.filter_tournaments(filter_service, unique_tournaments)
        export_info = WorkflowSteps.export_results(export_manager, final_tournaments, f"{sport.lower()}_comprehensive", export_files)
        
        # Create response objects
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = TournamentMetadata(
            total_found=len(final_tournaments), queries_used=len(queries), search_results=len(search_results),
            extraction_method="comprehensive_schema_based", timestamp=datetime.now().isoformat(), processing_time_seconds=processing_time
        )
        
        summary = ProcessingSummary(
            queries_generated=len(queries), search_results_collected=len(search_results), tournaments_extracted=len(tournaments),
            unique_tournaments=len(unique_tournaments), relevant_tournaments=len(final_tournaments),
            processing_pipeline="Generate→Search→Extract→Process→Filter→Export"
        )
        
        print(f"✅ Comprehensive workflow completed: {len(final_tournaments)} tournaments")
        return final_tournaments, metadata, export_info, summary
    
    def execute_quick(self, processing_engine, filter_service, export_manager, sport: str, level: str, export_files: bool = False) -> Tuple[List[Dict], TournamentMetadata, ExportInfo]:
        """Execute quick tournament workflow."""
        start_time = datetime.now()
        
        print(f"🔍 QUICK WORKFLOW: {sport} {level}")
        
        # Execute workflow steps (same steps, different configuration)
        queries = WorkflowSteps.generate_queries(processing_engine, sport)
        search_results = WorkflowSteps.collect_results(processing_engine, queries)
        tournaments = WorkflowSteps.extract_tournaments(processing_engine, search_results)
        unique_tournaments = WorkflowSteps.process_tournaments(processing_engine, tournaments)
        final_tournaments = WorkflowSteps.filter_tournaments(filter_service, unique_tournaments, level)
        export_info = WorkflowSteps.export_results(export_manager, final_tournaments, f"{sport.lower()}_api", export_files)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metadata = TournamentMetadata(
            total_found=len(final_tournaments), queries_used=len(queries), search_results=len(search_results),
            extraction_method="schema-based", timestamp=datetime.now().isoformat(), processing_time_seconds=processing_time
        )
        
        print(f"✅ Quick workflow completed: {len(final_tournaments)} tournaments")
        return final_tournaments, metadata, export_info
