#!/usr/bin/env python3
"""
API Response Models

Data models for API responses and request/response structure.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    """Processing status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    FAILED = "failed"


class ProcessingType(Enum):
    """Processing type enumeration."""
    QUICK_SEARCH = "quick_search"
    COMPREHENSIVE = "comprehensive_main_py_approach"
    HEALTH_CHECK = "health_check"


@dataclass
class TournamentMetadata:
    """Tournament processing metadata."""
    total_found: int
    queries_used: int
    search_results: int
    extraction_method: str
    timestamp: str
    processing_time_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExportInfo:
    """File export information."""
    status: str
    csv_file: Optional[str] = None
    json_file: Optional[str] = None
    export_timestamp: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessingSummary:
    """Processing pipeline summary."""
    queries_generated: int
    search_results_collected: int
    tournaments_extracted: int
    unique_tournaments: int
    relevant_tournaments: int
    processing_pipeline: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class APIResponse:
    """Standard API response structure."""
    status: ProcessingStatus
    message: str
    sport: Optional[str] = None
    processing_type: Optional[ProcessingType] = None
    tournaments: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[TournamentMetadata] = None
    export_info: Optional[ExportInfo] = None
    summary: Optional[ProcessingSummary] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for JSON serialization."""
        result = {
            "status": self.status.value if isinstance(self.status, ProcessingStatus) else self.status,
            "message": self.message
        }
        
        if self.sport:
            result["sport"] = self.sport
        
        if self.processing_type:
            result["processing_type"] = (
                self.processing_type.value 
                if isinstance(self.processing_type, ProcessingType) 
                else self.processing_type
            )
        
        if self.tournaments is not None:
            result["tournaments"] = self.tournaments
        
        if self.metadata:
            result["metadata"] = self.metadata.to_dict() if hasattr(self.metadata, 'to_dict') else self.metadata
        
        if self.export_info:
            result["export_info"] = self.export_info.to_dict() if hasattr(self.export_info, 'to_dict') else self.export_info
        
        if self.summary:
            result["summary"] = self.summary.to_dict() if hasattr(self.summary, 'to_dict') else self.summary
        
        if self.error:
            result["error"] = self.error
        
        return result


@dataclass
class HealthCheckResponse:
    """Health check response structure."""
    status: str
    timestamp: str
    version: str
    services: Dict[str, bool]
    configuration: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
