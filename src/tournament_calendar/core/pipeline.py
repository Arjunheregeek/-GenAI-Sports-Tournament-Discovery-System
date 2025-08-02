"""
Main Pipeline Orchestrator for Tournament Calendar System

This module provides the main pipeline class that orchestrates
the entire tournament data collection process.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .config import config
from ..extractors.query_generator import QueryGenerator
from ..extractors.search_collector import SearchCollector
from ..extractors.content_extractor import ContentExtractor
from ..processors.data_processor import TournamentDataProcessor
from ..database.database_manager import DatabaseManager
from ..exporters.data_exporter import DataExporter


class TournamentPipeline:
    """Main pipeline orchestrator for tournament data collection."""
    
    def __init__(self, custom_config: Optional[Dict] = None):
        """Initialize the pipeline with configuration."""
        self.config = config
        self.custom_config = custom_config or {}
        
        # Initialize components
        self.query_generator = None
        self.search_collector = None
        self.content_extractor = None
        self.data_processor = None
        self.database_manager = None
        self.data_exporter = None
        
        # Pipeline state
        self.pipeline_state = {
            'step_1_completed': False,
            'step_2_completed': False,
            'step_3_completed': False,
            'step_4_completed': False,
            'step_5_completed': False,
            'step_6_completed': False,
            'errors': [],
            'start_time': None,
            'end_time': None
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for the pipeline."""
        log_dir = self.config.OUTPUT_DIRECTORIES['logs']
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"pipeline_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Tournament Pipeline initialized")
    
    def validate_configuration(self) -> bool:
        """Validate pipeline configuration."""
        self.logger.info("Validating configuration...")
        
        errors = self.config.validate_config()
        if errors:
            self.logger.error(f"Configuration errors: {errors}")
            self.pipeline_state['errors'].extend(errors)
            return False
        
        self.logger.info("Configuration validation passed")
        return True
    
    def initialize_components(self):
        """Initialize all pipeline components."""
        self.logger.info("Initializing pipeline components...")
        
        try:
            # Initialize extractors
            self.query_generator = QueryGenerator(self.config)
            self.search_collector = SearchCollector(self.config)
            self.content_extractor = ContentExtractor(self.config)
            
            # Initialize processors
            self.data_processor = TournamentDataProcessor(self.config)
            
            # Initialize database manager
            self.database_manager = DatabaseManager(self.config)
            
            # Initialize data exporter
            self.data_exporter = DataExporter(self.config)
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize components: {str(e)}"
            self.logger.error(error_msg)
            self.pipeline_state['errors'].append(error_msg)
            raise
    
    def run_step_1(self) -> bool:
        """Step 1: Generate search queries."""
        self.logger.info("=" * 60)
        self.logger.info("🚀 Step 1: Query Generation")
        self.logger.info("=" * 60)
        
        try:
            queries = self.query_generator.generate_all_queries()
            if queries:
                self.pipeline_state['step_1_completed'] = True
                self.logger.info(f"✅ Step 1 completed: {len(queries)} queries generated")
                return True
            else:
                error_msg = "No queries generated in Step 1"
                self.logger.error(f"❌ {error_msg}")
                self.pipeline_state['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step 1 failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.pipeline_state['errors'].append(error_msg)
            return False
    
    def run_step_2(self) -> bool:
        """Step 2: Collect search results."""
        self.logger.info("=" * 60)
        self.logger.info("🔍 Step 2: Search Results Collection")
        self.logger.info("=" * 60)
        
        try:
            search_results = self.search_collector.collect_all_results()
            if search_results:
                self.pipeline_state['step_2_completed'] = True
                self.logger.info(f"✅ Step 2 completed: {len(search_results)} results collected")
                return True
            else:
                error_msg = "No search results collected in Step 2"
                self.logger.error(f"❌ {error_msg}")
                self.pipeline_state['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step 2 failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.pipeline_state['errors'].append(error_msg)
            return False
    
    def run_step_3(self) -> bool:
        """Step 3: Extract content from web pages."""
        self.logger.info("=" * 60)
        self.logger.info("🌐 Step 3: Content Extraction")
        self.logger.info("=" * 60)
        
        try:
            extracted_content = self.content_extractor.extract_all_content()
            if extracted_content:
                self.pipeline_state['step_3_completed'] = True
                self.logger.info(f"✅ Step 3 completed: {len(extracted_content)} pages extracted")
                return True
            else:
                error_msg = "No content extracted in Step 3"
                self.logger.error(f"❌ {error_msg}")
                self.pipeline_state['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step 3 failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.pipeline_state['errors'].append(error_msg)
            return False
    
    def run_step_4(self) -> bool:
        """Step 4: Process tournament data."""
        self.logger.info("=" * 60)
        self.logger.info("🎯 Step 4: Tournament Data Processing")
        self.logger.info("=" * 60)
        
        try:
            tournaments = self.data_processor.process_all_content()
            if tournaments:
                self.pipeline_state['step_4_completed'] = True
                self.logger.info(f"✅ Step 4 completed: {len(tournaments)} tournaments processed")
                return True
            else:
                error_msg = "No tournaments processed in Step 4"
                self.logger.error(f"❌ {error_msg}")
                self.pipeline_state['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step 4 failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.pipeline_state['errors'].append(error_msg)
            return False
    
    def run_step_5(self) -> bool:
        """Step 5: Database operations."""
        self.logger.info("=" * 60)
        self.logger.info("📥 Step 5: Database Operations")
        self.logger.info("=" * 60)
        
        try:
            success = self.database_manager.store_all_tournaments()
            if success:
                self.pipeline_state['step_5_completed'] = True
                self.logger.info("✅ Step 5 completed: Data stored in database")
                return True
            else:
                error_msg = "Database operations failed in Step 5"
                self.logger.error(f"❌ {error_msg}")
                self.pipeline_state['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step 5 failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.pipeline_state['errors'].append(error_msg)
            return False
    
    def run_step_6(self) -> bool:
        """Step 6: Final export and API."""
        self.logger.info("=" * 60)
        self.logger.info("📤 Step 6: Final Export and API")
        self.logger.info("=" * 60)
        
        try:
            export_files = self.data_exporter.export_all_formats()
            if export_files:
                self.pipeline_state['step_6_completed'] = True
                self.logger.info(f"✅ Step 6 completed: {len(export_files)} files exported")
                return True
            else:
                error_msg = "Export failed in Step 6"
                self.logger.error(f"❌ {error_msg}")
                self.pipeline_state['errors'].append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step 6 failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.pipeline_state['errors'].append(error_msg)
            return False
    
    def run_full_pipeline(self, skip_steps: List[int] = None) -> Dict[str, Any]:
        """Run the complete pipeline."""
        self.logger.info("🚀 Starting Full Tournament Calendar Pipeline")
        self.pipeline_state['start_time'] = datetime.now()
        
        skip_steps = skip_steps or []
        
        # Validate configuration
        if not self.validate_configuration():
            return self.get_pipeline_summary()
        
        # Initialize components
        try:
            self.initialize_components()
        except Exception as e:
            return self.get_pipeline_summary()
        
        # Run pipeline steps
        pipeline_steps = [
            (1, self.run_step_1, "Query Generation"),
            (2, self.run_step_2, "Search Results Collection"),
            (3, self.run_step_3, "Content Extraction"),
            (4, self.run_step_4, "Tournament Data Processing"),
            (5, self.run_step_5, "Database Operations"),
            (6, self.run_step_6, "Final Export and API")
        ]
        
        for step_num, step_func, step_name in pipeline_steps:
            if step_num in skip_steps:
                self.logger.info(f"⏭️  Skipping Step {step_num}: {step_name}")
                continue
            
            success = step_func()
            if not success:
                self.logger.error(f"❌ Pipeline stopped at Step {step_num}")
                break
        
        self.pipeline_state['end_time'] = datetime.now()
        
        # Generate final summary
        summary = self.get_pipeline_summary()
        self.logger.info("🎉 Pipeline execution completed")
        
        return summary
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Get comprehensive pipeline execution summary."""
        summary = {
            'execution_time': None,
            'steps_completed': sum([
                self.pipeline_state['step_1_completed'],
                self.pipeline_state['step_2_completed'],
                self.pipeline_state['step_3_completed'],
                self.pipeline_state['step_4_completed'],
                self.pipeline_state['step_5_completed'],
                self.pipeline_state['step_6_completed']
            ]),
            'total_steps': 6,
            'success_rate': 0,
            'errors': self.pipeline_state['errors'],
            'step_status': {
                'step_1_query_generation': self.pipeline_state['step_1_completed'],
                'step_2_search_collection': self.pipeline_state['step_2_completed'],
                'step_3_content_extraction': self.pipeline_state['step_3_completed'],
                'step_4_data_processing': self.pipeline_state['step_4_completed'],
                'step_5_database_operations': self.pipeline_state['step_5_completed'],
                'step_6_export_api': self.pipeline_state['step_6_completed']
            }
        }
        
        if self.pipeline_state['start_time'] and self.pipeline_state['end_time']:
            execution_time = self.pipeline_state['end_time'] - self.pipeline_state['start_time']
            summary['execution_time'] = str(execution_time)
        
        summary['success_rate'] = (summary['steps_completed'] / summary['total_steps']) * 100
        
        return summary
    
    def run_single_step(self, step_number: int) -> bool:
        """Run a single pipeline step."""
        if not self.validate_configuration():
            return False
        
        try:
            self.initialize_components()
        except Exception:
            return False
        
        step_functions = {
            1: self.run_step_1,
            2: self.run_step_2,
            3: self.run_step_3,
            4: self.run_step_4,
            5: self.run_step_5,
            6: self.run_step_6
        }
        
        if step_number not in step_functions:
            self.logger.error(f"Invalid step number: {step_number}")
            return False
        
        return step_functions[step_number]()
    
    def cleanup(self):
        """Cleanup pipeline resources."""
        self.logger.info("Cleaning up pipeline resources...")
        
        # Close database connections
        if self.database_manager:
            self.database_manager.close_connections()
        
        # Clear temporary files if needed
        # Add cleanup logic here
        
        self.logger.info("Pipeline cleanup completed")
