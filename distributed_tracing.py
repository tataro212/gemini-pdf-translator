"""
Distributed Tracing Implementation for PDF Translation Pipeline

This implements Proposition 3: Leverage Distributed Tracing
Provides comprehensive tracing across all pipeline components with metadata tracking.
"""

import uuid
import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from enum import Enum

logger = logging.getLogger(__name__)

class SpanType(Enum):
    """Types of spans in the translation pipeline"""
    DOCUMENT_PROCESSING = "document_processing"
    IMAGE_EXTRACTION = "image_extraction"
    CONTENT_EXTRACTION = "content_extraction"
    TRANSLATION = "translation"
    DOCUMENT_GENERATION = "document_generation"
    VALIDATION = "validation"
    CACHE_OPERATION = "cache_operation"

@dataclass
class SpanMetadata:
    """Metadata attached to spans for detailed tracking"""
    image_placeholders_found: int = 0
    image_placeholders_preserved: int = 0
    document_model: str = "unknown"
    content_blocks_count: int = 0
    translation_method: str = "unknown"
    ocr_engine_used: str = "unknown"
    cache_hit: bool = False
    file_size_bytes: int = 0
    processing_time_ms: float = 0.0
    error_count: int = 0
    validation_passed: bool = True

@dataclass
class Span:
    """Individual span in the distributed trace"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    span_type: SpanType
    start_time: float
    end_time: Optional[float] = None
    metadata: SpanMetadata = None
    tags: Dict[str, Any] = None
    logs: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = SpanMetadata()
        if self.tags is None:
            self.tags = {}
        if self.logs is None:
            self.logs = []
    
    @property
    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds"""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span"""
        self.tags[key] = value
    
    def add_log(self, message: str, level: str = "INFO", **kwargs):
        """Add a log entry to the span"""
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)
    
    def finish(self):
        """Mark the span as finished"""
        self.end_time = time.time()
        self.metadata.processing_time_ms = self.duration_ms

class DistributedTracer:
    """
    Distributed tracing system for PDF translation pipeline.
    
    Tracks the complete lifecycle of document translation with detailed metadata
    to enable rapid debugging and performance analysis.
    """
    
    def __init__(self):
        self.active_traces: Dict[str, List[Span]] = {}
        self.completed_traces: Dict[str, List[Span]] = {}
        self.current_span: Optional[Span] = None
        self.current_trace_id: Optional[str] = None
    
    def start_trace(self, operation_name: str, document_path: str = None) -> str:
        """Start a new distributed trace for a document translation"""
        trace_id = str(uuid.uuid4())
        self.current_trace_id = trace_id
        self.active_traces[trace_id] = []
        
        # Create root span
        root_span = self.start_span(
            operation_name=operation_name,
            span_type=SpanType.DOCUMENT_PROCESSING,
            trace_id=trace_id
        )
        
        if document_path:
            root_span.add_tag("document_path", document_path)
            root_span.add_tag("document_name", document_path.split("/")[-1] if "/" in document_path else document_path)
        
        logger.info(f"🔍 Started distributed trace: {trace_id} for {operation_name}")
        return trace_id
    
    def start_span(self, operation_name: str, span_type: SpanType, 
                   trace_id: str = None, parent_span_id: str = None) -> Span:
        """Start a new span within a trace"""
        if trace_id is None:
            trace_id = self.current_trace_id
        
        if trace_id is None:
            raise ValueError("No active trace. Call start_trace() first.")
        
        span_id = str(uuid.uuid4())
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id or (self.current_span.span_id if self.current_span else None),
            operation_name=operation_name,
            span_type=span_type,
            start_time=time.time()
        )
        
        self.active_traces[trace_id].append(span)
        self.current_span = span
        
        logger.debug(f"📊 Started span: {operation_name} ({span_id})")
        return span
    
    def finish_span(self, span: Span = None):
        """Finish the current or specified span"""
        if span is None:
            span = self.current_span
        
        if span is None:
            logger.warning("No active span to finish")
            return
        
        span.finish()
        logger.debug(f"✅ Finished span: {span.operation_name} ({span.duration_ms:.2f}ms)")
        
        # Update current span to parent
        if span == self.current_span:
            parent_span = self.find_span_by_id(span.parent_span_id, span.trace_id)
            self.current_span = parent_span
    
    def finish_trace(self, trace_id: str = None):
        """Finish a trace and move it to completed traces"""
        if trace_id is None:
            trace_id = self.current_trace_id
        
        if trace_id not in self.active_traces:
            logger.warning(f"Trace {trace_id} not found in active traces")
            return
        
        # Finish any remaining active spans
        for span in self.active_traces[trace_id]:
            if span.end_time is None:
                span.finish()
        
        # Move to completed traces
        self.completed_traces[trace_id] = self.active_traces.pop(trace_id)
        
        if trace_id == self.current_trace_id:
            self.current_trace_id = None
            self.current_span = None
        
        logger.info(f"🏁 Finished trace: {trace_id}")
        self.generate_trace_summary(trace_id)
    
    def find_span_by_id(self, span_id: str, trace_id: str) -> Optional[Span]:
        """Find a span by its ID within a trace"""
        if trace_id in self.active_traces:
            for span in self.active_traces[trace_id]:
                if span.span_id == span_id:
                    return span
        
        if trace_id in self.completed_traces:
            for span in self.completed_traces[trace_id]:
                if span.span_id == span_id:
                    return span
        
        return None
    
    @contextmanager
    def span(self, operation_name: str, span_type: SpanType, **metadata):
        """Context manager for automatic span lifecycle management"""
        span = self.start_span(operation_name, span_type)
        
        # Add metadata
        for key, value in metadata.items():
            if hasattr(span.metadata, key):
                setattr(span.metadata, key, value)
            else:
                span.add_tag(key, value)
        
        try:
            yield span
        except Exception as e:
            span.add_log(f"Error: {str(e)}", level="ERROR")
            span.metadata.error_count += 1
            span.metadata.validation_passed = False
            raise
        finally:
            self.finish_span(span)
    
    def add_metadata_to_current_span(self, **metadata):
        """Add metadata to the current active span"""
        if self.current_span is None:
            logger.warning("No active span to add metadata to")
            return
        
        for key, value in metadata.items():
            if hasattr(self.current_span.metadata, key):
                setattr(self.current_span.metadata, key, value)
            else:
                self.current_span.add_tag(key, value)
    
    def generate_trace_summary(self, trace_id: str):
        """Generate a comprehensive summary of a completed trace"""
        if trace_id not in self.completed_traces:
            logger.warning(f"Trace {trace_id} not found in completed traces")
            return
        
        spans = self.completed_traces[trace_id]
        root_span = next((span for span in spans if span.parent_span_id is None), None)
        
        if not root_span:
            logger.warning(f"No root span found for trace {trace_id}")
            return
        
        # Calculate total duration
        total_duration = root_span.duration_ms
        
        # Aggregate metadata
        total_images_found = sum(span.metadata.image_placeholders_found for span in spans)
        total_images_preserved = sum(span.metadata.image_placeholders_preserved for span in spans)
        total_content_blocks = max(span.metadata.content_blocks_count for span in spans)
        
        # Count span types
        span_type_counts = {}
        for span in spans:
            span_type = span.span_type.value
            span_type_counts[span_type] = span_type_counts.get(span_type, 0) + 1
        
        # Check for data loss
        image_preservation_rate = (total_images_preserved / total_images_found * 100) if total_images_found > 0 else 100
        
        summary = f"""
🔍 DISTRIBUTED TRACE SUMMARY
============================
Trace ID: {trace_id}
Total Duration: {total_duration:.2f}ms

📊 PIPELINE OVERVIEW:
• Total Spans: {len(spans)}
• Content Blocks: {total_content_blocks}
• Images Found: {total_images_found}
• Images Preserved: {total_images_preserved}
• Preservation Rate: {image_preservation_rate:.1f}%

📋 SPAN BREAKDOWN:
"""
        
        for span_type, count in span_type_counts.items():
            summary += f"• {span_type.replace('_', ' ').title()}: {count}\n"
        
        # Identify potential issues
        issues = []
        if image_preservation_rate < 100:
            issues.append(f"Image loss detected: {total_images_found - total_images_preserved} images lost")
        
        error_spans = [span for span in spans if span.metadata.error_count > 0]
        if error_spans:
            issues.append(f"Errors in {len(error_spans)} spans")
        
        if issues:
            summary += f"\n⚠️ POTENTIAL ISSUES:\n"
            for issue in issues:
                summary += f"• {issue}\n"
        
        # Performance insights
        slowest_span = max(spans, key=lambda s: s.duration_ms)
        summary += f"""
⚡ PERFORMANCE INSIGHTS:
• Slowest Operation: {slowest_span.operation_name} ({slowest_span.duration_ms:.2f}ms)
• Average Span Duration: {sum(s.duration_ms for s in spans) / len(spans):.2f}ms
"""
        
        logger.info(summary)
    
    def export_trace_json(self, trace_id: str) -> str:
        """Export trace data as JSON for external analysis"""
        if trace_id not in self.completed_traces:
            return "{}"
        
        spans = self.completed_traces[trace_id]
        trace_data = {
            "trace_id": trace_id,
            "spans": [
                {
                    "span_id": span.span_id,
                    "parent_span_id": span.parent_span_id,
                    "operation_name": span.operation_name,
                    "span_type": span.span_type.value,
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                    "duration_ms": span.duration_ms,
                    "metadata": asdict(span.metadata),
                    "tags": span.tags,
                    "logs": span.logs
                }
                for span in spans
            ]
        }
        
        return json.dumps(trace_data, indent=2)

# Global tracer instance
tracer = DistributedTracer()

# Convenience functions
def start_trace(operation_name: str, document_path: str = None) -> str:
    """Start a new distributed trace"""
    return tracer.start_trace(operation_name, document_path)

def start_span(operation_name: str, span_type: SpanType) -> Span:
    """Start a new span"""
    return tracer.start_span(operation_name, span_type)

def finish_span(span: Span = None):
    """Finish a span"""
    tracer.finish_span(span)

def finish_trace(trace_id: str = None):
    """Finish a trace"""
    tracer.finish_trace(trace_id)

def span(operation_name: str, span_type: SpanType, **metadata):
    """Context manager for spans"""
    return tracer.span(operation_name, span_type, **metadata)

def add_metadata(**metadata):
    """Add metadata to current span"""
    tracer.add_metadata_to_current_span(**metadata)
