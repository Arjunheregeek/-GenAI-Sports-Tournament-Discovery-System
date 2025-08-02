#!/usr/bin/env python3
"""
Workflow Executor Module

Executes workflow steps and manages workflow state.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use relative imports
try:
    from ..models import TournamentMetadata, ExportInfo, ProcessingSummary
    from .workflow_steps import (
        QueryGenerationStep, SearchCollectionStep, TournamentExtractionStep,
        DeduplicationStep, FilteringStep, ExportStep
    )
except ImportError:
    from api.models import TournamentMetadata, ExportInfo, ProcessingSummary
    from api.services.workflow_steps import (
        QueryGenerationStep, SearchCollectionStep, TournamentExtractionStep,
        DeduplicationStep, FilteringStep, ExportStep
    )


class WorkflowExecutor:
    """Executes tournament processing workflows."""
    
    def __init__(self):
        """Initialize workflow executor."""
        self.steps = []
        self.start_time = None
        self.end_time = None
    
    def execute_comprehensive_workflow(
        self,
        processing_engine,
        filter_service, 
        export_manager,
        sport: str,
        export_files: bool = True
    ) -> Tuple[List[Dict], TournamentMetadata, ExportInfo, ProcessingSummary]:
        """Execute comprehensive workflow."""
        
        self.start_time = datetime.now()
        print(f"🚀 COMPREHENSIVE WORKFLOW: {sport} tournaments")
        print("=" * 70)
        
        # Initialize steps
        steps = [
            QueryGenerationStep(),
            SearchCollectionStep(), 
            TournamentExtractionStep(),
            DeduplicationStep(),
            FilteringStep(),
            ExportStep()
        ]
        
        # Execute workflow
        sport_queries = steps[0].execute(processing_engine, sport)
        all_search_results = steps[1].execute(processing_engine, sport_queries, 8)
        tournaments = steps[2].execute(processing_engine, all_search_results, None)
        unique_tournaments = steps[3].execute(processing_engine, tournaments)
        relevant_tournaments = steps[4].execute(filter_service, unique_tournaments)
        export_info = steps[5].execute(export_manager, relevant_tournaments, f"{sport.lower()}_comprehensive", export_files)
        
        # Calculate processing time
        self.end_time = datetime.now()
        processing_time = (self.end_time - self.start_time).total_seconds()
        
        # Create metadata and summary
        metadata = TournamentMetadata(
            total_found=len(relevant_tournaments),
            queries_used=len(sport_queries),
            search_results=len(all_search_results),
            extraction_method="comprehensive_schema_based",
            timestamp=self.end_time.isoformat(),
            processing_time_seconds=processing_time
        )
        
        summary = ProcessingSummary(
            queries_generated=len(sport_queries),
            search_results_collected=len(all_search_results),
            tournaments_extracted=len(tournaments),
            unique_tournaments=len(unique_tournaments),
            relevant_tournaments=len(relevant_tournaments),
            processing_pipeline="Generate→Search→Extract→Deduplicate→Filter→Export"
        )
        
        print(f"\n🎉 COMPREHENSIVE WORKFLOW COMPLETED!")
        print(f"📊 Summary: {len(sport_queries)} queries → {len(all_search_results)} results → {len(relevant_tournaments)} tournaments")
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        
        return relevant_tournaments, metadata, export_info, summary
    
    def execute_quick_workflow(
        self,
        processing_engine,
        filter_service,
        export_manager, 
        sport: str,
        level: str = "International",
        export_files: bool = False
    ) -> Tuple[List[Dict], TournamentMetadata, ExportInfo]:
        """Execute quick workflow."""
        
        self.start_time = datetime.now()
        print(f"🔍 QUICK WORKFLOW: {sport} {level} tournaments")
        print("-" * 50)
        
        # Execute streamlined workflow
        step1 = QueryGenerationStep()
        step2 = SearchCollectionStep()
        step3 = TournamentExtractionStep()
        step4 = DeduplicationStep()
        step5 = FilteringStep()
        step6 = ExportStep()
        
        sport_queries = step1.execute(processing_engine, sport)
        all_search_results = step2.execute(processing_engine, sport_queries, 8)
        tournaments = step3.execute(processing_engine, all_search_results, None)
        unique_tournaments = step4.execute(processing_engine, tournaments)
        relevant_tournaments = step5.execute(filter_service, unique_tournaments, level)
        export_info = step6.execute(export_manager, relevant_tournaments, f"{sport.lower()}_tournaments_api", export_files)
        
        # Calculate processing time
        self.end_time = datetime.now()
        processing_time = (self.end_time - self.start_time).total_seconds()
        
        # Create metadata
        metadata = TournamentMetadata(
            total_found=len(relevant_tournaments),
            queries_used=len(sport_queries),
            search_results=len(all_search_results),
            extraction_method="schema-based",
            timestamp=self.end_time.isoformat(),
            processing_time_seconds=processing_time
        )
        
        print(f"✅ Quick workflow completed: {len(relevant_tournaments)} tournaments found")
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        
        return relevant_tournaments, metadata, export_info
