"""
Pipeline tests for Tournament Calendar System.

Tests the main pipeline orchestration and individual step execution.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from tournament_calendar.core.pipeline import TournamentPipeline


class TestTournamentPipeline:
    """Test the main pipeline orchestrator."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly."""
        pipeline = TournamentPipeline()
        
        assert pipeline is not None
        assert hasattr(pipeline, 'config')
        assert hasattr(pipeline, 'query_generator')
        assert hasattr(pipeline, 'search_collector')
    
    def test_single_step_execution(self):
        """Test individual step execution."""
        pipeline = TournamentPipeline()
        
        # Mock the step methods
        with patch.object(pipeline, '_run_step_1', return_value=True) as mock_step:
            result = pipeline.run_single_step(1)
            assert result is True
            mock_step.assert_called_once()
    
    def test_invalid_step_number(self):
        """Test handling of invalid step numbers."""
        pipeline = TournamentPipeline()
        
        # Test invalid step numbers
        with pytest.raises(ValueError):
            pipeline.run_single_step(0)
        
        with pytest.raises(ValueError):
            pipeline.run_single_step(7)
    
    def test_full_pipeline_execution(self):
        """Test full pipeline execution."""
        pipeline = TournamentPipeline()
        
        # Mock all step methods to return True
        step_methods = [
            '_run_step_1', '_run_step_2', '_run_step_3',
            '_run_step_4', '_run_step_5', '_run_step_6'
        ]
        
        with patch.multiple(
            pipeline,
            **{method: Mock(return_value=True) for method in step_methods}
        ):
            summary = pipeline.run_full_pipeline()
            
            assert summary['steps_completed'] == 6
            assert summary['total_steps'] == 6
            assert summary['success_rate'] == 100.0
            assert len(summary['errors']) == 0
    
    def test_pipeline_with_skip_steps(self):
        """Test pipeline execution with skip steps."""
        pipeline = TournamentPipeline()
        
        step_methods = [
            '_run_step_1', '_run_step_2', '_run_step_3',
            '_run_step_4', '_run_step_5', '_run_step_6'
        ]
        
        with patch.multiple(
            pipeline,
            **{method: Mock(return_value=True) for method in step_methods}
        ):
            # Skip steps 2 and 4
            summary = pipeline.run_full_pipeline(skip_steps=[2, 4])
            
            assert summary['steps_completed'] == 4
            assert summary['total_steps'] == 6
            assert summary['success_rate'] == pytest.approx(66.7, rel=0.1)
    
    def test_pipeline_with_failures(self):
        """Test pipeline handling of step failures."""
        pipeline = TournamentPipeline()
        
        # Mock steps with some failures
        with patch.multiple(
            pipeline,
            _run_step_1=Mock(return_value=True),
            _run_step_2=Mock(return_value=False),
            _run_step_3=Mock(return_value=True),
            _run_step_4=Mock(return_value=False),
            _run_step_5=Mock(return_value=True),
            _run_step_6=Mock(return_value=True)
        ):
            summary = pipeline.run_full_pipeline()
            
            assert summary['steps_completed'] == 4
            assert summary['total_steps'] == 6
            assert summary['success_rate'] == pytest.approx(66.7, rel=0.1)
            assert len(summary['errors']) == 2


class TestStepExecution:
    """Test individual step execution logic."""
    
    def test_step_1_query_generation(self):
        """Test step 1 (query generation)."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline.query_generator, 'generate_all_queries', return_value=True):
            result = pipeline._run_step_1()
            assert result is True
    
    def test_step_2_search_collection(self):
        """Test step 2 (search collection)."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline.search_collector, 'collect_all_data', return_value=True):
            result = pipeline._run_step_2()
            assert result is True
    
    def test_step_3_content_extraction(self):
        """Test step 3 (content extraction)."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline.content_extractor, 'extract_all_content', return_value=True):
            result = pipeline._run_step_3()
            assert result is True
    
    def test_step_4_data_processing(self):
        """Test step 4 (data processing)."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline.data_processor, 'process_all_data', return_value=True):
            result = pipeline._run_step_4()
            assert result is True
    
    def test_step_5_database_operations(self):
        """Test step 5 (database operations)."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline.database_manager, 'store_all_data', return_value=True):
            result = pipeline._run_step_5()
            assert result is True
    
    def test_step_6_export_api(self):
        """Test step 6 (export and API)."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline.data_exporter, 'export_all_data', return_value=True):
            result = pipeline._run_step_6()
            assert result is True


class TestErrorHandling:
    """Test error handling in pipeline execution."""
    
    def test_step_exception_handling(self):
        """Test that step exceptions are properly handled."""
        pipeline = TournamentPipeline()
        
        # Mock a step to raise an exception
        with patch.object(
            pipeline.query_generator, 
            'generate_all_queries', 
            side_effect=Exception("Test error")
        ):
            result = pipeline._run_step_1()
            assert result is False
    
    def test_pipeline_continues_after_step_failure(self):
        """Test that pipeline continues execution after step failures."""
        pipeline = TournamentPipeline()
        
        # Mock first step to fail, others to succeed
        with patch.multiple(
            pipeline,
            _run_step_1=Mock(side_effect=Exception("Step 1 failed")),
            _run_step_2=Mock(return_value=True),
            _run_step_3=Mock(return_value=True),
            _run_step_4=Mock(return_value=True),
            _run_step_5=Mock(return_value=True),
            _run_step_6=Mock(return_value=True)
        ):
            summary = pipeline.run_full_pipeline()
            
            # Should complete 5 steps despite first step failure
            assert summary['steps_completed'] == 5
            assert len(summary['errors']) == 1


class TestPipelineIntegration:
    """Integration tests for pipeline components."""
    
    def test_pipeline_state_management(self):
        """Test that pipeline maintains state between steps."""
        pipeline = TournamentPipeline()
        
        # Test that pipeline tracks execution state
        assert hasattr(pipeline, 'execution_state')
        
        # Mock successful step execution
        with patch.object(pipeline, '_run_step_1', return_value=True):
            pipeline.run_single_step(1)
            assert pipeline.execution_state['step_1_query_generation'] is True
    
    def test_pipeline_logging(self):
        """Test that pipeline logs execution properly."""
        pipeline = TournamentPipeline()
        
        with patch('tournament_calendar.core.pipeline.logger') as mock_logger:
            with patch.object(pipeline, '_run_step_1', return_value=True):
                pipeline.run_single_step(1)
                
                # Verify logging calls were made
                mock_logger.info.assert_called()
    
    def test_pipeline_timing(self):
        """Test that pipeline tracks execution time."""
        pipeline = TournamentPipeline()
        
        with patch.object(pipeline, '_run_step_1', return_value=True):
            summary = pipeline.run_full_pipeline()
            
            # Should have execution time recorded
            assert 'execution_time' in summary
            assert summary['execution_time'] is not None
