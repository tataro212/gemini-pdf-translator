"""
Unified Configuration System using Pydantic for Type Safety and Validation

This module replaces the fragmented config.ini and config_enhanced.ini files
with a single, typed, validated configuration system.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, model_validator
import logging

logger = logging.getLogger(__name__)

class GeneralSettings(BaseModel):
    """General application settings"""
    target_language: str = Field(default="Spanish", description="Target language for translation")
    nougat_only_mode: bool = Field(default=False, description="Use Nougat-only processing mode")
    use_advanced_features: bool = Field(default=True, description="Enable advanced translation features")
    debug_mode: bool = Field(default=False, description="Enable debug logging")
    
    @validator('target_language')
    def validate_target_language(cls, v):
        valid_languages = [
            'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Chinese', 
            'Japanese', 'Korean', 'Russian', 'Arabic', 'Hindi', 'Dutch'
        ]
        if v not in valid_languages:
            logger.warning(f"Target language '{v}' not in validated list: {valid_languages}")
        return v

class PerformanceSettings(BaseModel):
    """Performance and parallel processing settings"""
    max_parallel_workers: int = Field(default=4, ge=1, le=16, description="Maximum parallel workers for page processing")
    enable_parallel_processing: bool = Field(default=True, description="Enable parallel page processing")
    chunk_size: int = Field(default=1000, ge=100, le=10000, description="Text chunk size for processing")
    max_memory_usage_mb: int = Field(default=2048, ge=512, le=8192, description="Maximum memory usage in MB")

class MonitoringSettings(BaseModel):
    """Monitoring and logging settings"""
    enable_structured_metrics: bool = Field(default=True, description="Enable structured JSON metrics logging")
    enable_distributed_tracing: bool = Field(default=True, description="Enable distributed tracing")
    log_level: str = Field(default="INFO", description="Logging level")
    metrics_output_file: Optional[str] = Field(default=None, description="File to write metrics to")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

class PDFProcessingSettings(BaseModel):
    """PDF processing configuration"""
    extract_cover_page: bool = Field(default=True, description="Extract cover page separately")
    extract_images: bool = Field(default=True, description="Extract images from PDF")
    image_quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum image quality threshold")
    max_image_size_mb: int = Field(default=10, ge=1, le=50, description="Maximum image size in MB")
    ocr_confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="OCR confidence threshold")

class TranslationSettings(BaseModel):
    """Translation service configuration"""
    service_provider: str = Field(default="gemini", description="Translation service provider")
    api_key: Optional[str] = Field(default=None, description="API key for translation service")
    model_name: str = Field(default="gemini-2.0-flash-exp", description="Model name for translation")
    max_tokens_per_request: int = Field(default=4000, ge=100, le=32000, description="Maximum tokens per request")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Translation temperature")
    enable_caching: bool = Field(default=True, description="Enable translation caching")
    
    @validator('service_provider')
    def validate_service_provider(cls, v):
        valid_providers = ['gemini', 'openai', 'anthropic', 'deepl']
        if v.lower() not in valid_providers:
            raise ValueError(f"Service provider must be one of: {valid_providers}")
        return v.lower()

class QuarantineSettings(BaseModel):
    """Quarantine system configuration"""
    max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts before quarantine")
    quarantine_directory: str = Field(default="quarantine", description="Directory for quarantined files")
    auto_cleanup_days: int = Field(default=30, ge=1, le=365, description="Days to keep quarantined files")

class IntelligentPipelineSettings(BaseModel):
    """Intelligent pipeline configuration"""
    use_intelligent_pipeline: bool = Field(default=True, description="Enable intelligent processing pipeline")
    max_concurrent_tasks: int = Field(default=4, ge=1, le=16, description="Maximum concurrent tasks")
    content_analysis_depth: str = Field(default="medium", description="Content analysis depth")
    
    @validator('content_analysis_depth')
    def validate_analysis_depth(cls, v):
        valid_depths = ['shallow', 'medium', 'deep']
        if v.lower() not in valid_depths:
            raise ValueError(f"Analysis depth must be one of: {valid_depths}")
        return v.lower()

class UnifiedConfig(BaseModel):
    """Main configuration class containing all settings"""
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    pdf_processing: PDFProcessingSettings = Field(default_factory=PDFProcessingSettings)
    translation: TranslationSettings = Field(default_factory=TranslationSettings)
    quarantine: QuarantineSettings = Field(default_factory=QuarantineSettings)
    intelligent_pipeline: IntelligentPipelineSettings = Field(default_factory=IntelligentPipelineSettings)
    
    class Config:
        extra = "forbid"  # Prevent unknown fields
        validate_assignment = True  # Validate on assignment
        
    @model_validator(mode='before')
    @classmethod
    def validate_config_consistency(cls, values):
        """Validate configuration consistency across sections"""
        if isinstance(values, dict):
            performance = values.get('performance', {})
            intelligent = values.get('intelligent_pipeline', {})

            # Ensure parallel workers don't exceed concurrent tasks
            if isinstance(performance, dict) and isinstance(intelligent, dict):
                max_workers = performance.get('max_parallel_workers', 4)
                max_tasks = intelligent.get('max_concurrent_tasks', 4)

                if max_workers > max_tasks * 2:
                    logger.warning(f"max_parallel_workers ({max_workers}) is much higher than max_concurrent_tasks ({max_tasks})")

        return values

class ConfigManager:
    """Unified configuration manager with validation and type safety"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config: Optional[UnifiedConfig] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self.config = UnifiedConfig(**config_data)
                logger.info(f"✅ Configuration loaded from {self.config_file}")
            else:
                logger.info(f"📝 Creating default configuration at {self.config_file}")
                self.config = UnifiedConfig()
                self.save_config()
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            logger.info("🔄 Using default configuration")
            self.config = UnifiedConfig()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.model_dump(), f, indent=2)
            logger.info(f"💾 Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
    
    def get_value(self, section: str, key: str, default=None):
        """Get a configuration value with dot notation support"""
        try:
            section_obj = getattr(self.config, section.lower())
            return getattr(section_obj, key, default)
        except AttributeError:
            logger.warning(f"Configuration key not found: {section}.{key}")
            return default
    
    def set_value(self, section: str, key: str, value):
        """Set a configuration value with validation"""
        try:
            section_obj = getattr(self.config, section.lower())
            setattr(section_obj, key, value)
            logger.info(f"✅ Configuration updated: {section}.{key} = {value}")
        except Exception as e:
            logger.error(f"❌ Failed to set configuration: {section}.{key} = {value}: {e}")
    
    def validate_config(self) -> bool:
        """Validate the entire configuration"""
        try:
            # Re-validate the configuration
            self.config = UnifiedConfig(**self.config.model_dump())
            logger.info("✅ Configuration validation passed")
            return True
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    def get_legacy_config_value(self, section: str, key: str, default=None, value_type=str):
        """Legacy compatibility method for existing code"""
        value = self.get_value(section, key, default)

        # Type conversion for legacy compatibility
        if value_type == bool and isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        elif value_type == int and not isinstance(value, int):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif value_type == float and not isinstance(value, float):
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        return value

    def get_config_value(self, section: str, key: str, default=None, value_type=str):
        """Legacy compatibility method - alias for get_legacy_config_value"""
        return self.get_legacy_config_value(section, key, default, value_type)

    @property
    def translation_enhancement_settings(self):
        """Legacy compatibility property for translation enhancement settings"""
        return {
            'target_language': self.config.general.target_language,
            'use_glossary': False,  # Not implemented in unified config yet
            'glossary_file_path': "glossary.json",
            'use_translation_cache': self.config.translation.enable_caching,
            'translation_cache_file_path': "translation_cache.json",  # Default cache file
            'use_advanced_features': self.config.general.use_advanced_features,
            'enable_easyocr': False,  # Not implemented in unified config yet
            'perform_quality_assessment': True,  # Default value
            'qa_strategy': 'full',  # Default value
            'qa_sample_percentage': 0.1  # Default value
        }

    @property
    def gemini_settings(self):
        """Legacy compatibility property for Gemini API settings"""
        model_name = self.config.translation.model_name
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        return {
            'model_name': model_name,
            'temperature': self.config.translation.temperature,
            'max_tokens': self.config.translation.max_tokens_per_request,
            'max_concurrent_calls': 5,  # Default value
            'timeout': 600,  # Default value
            'api_key': self.config.translation.api_key
        }

    @property
    def optimization_settings(self):
        """Legacy compatibility property for optimization settings"""
        return {
            'enable_parallel_processing': True,  # Default value
            'max_concurrent_tasks': self.config.intelligent_pipeline.max_concurrent_tasks,
            'enable_caching': self.config.translation.enable_caching,
            'cache_ttl': 86400,  # Default 24 hours
            'enable_compression': True,  # Default value
            'compression_level': 6,  # Default value
            'enable_metrics': True,  # Default value
            'metrics_interval': 60,  # Default value
            'enable_profiling': False,  # Default value
            'memory_limit_mb': 2048,  # Default value
            'disk_cache_size_mb': 1024,  # Default value
            'cleanup_interval': 3600  # Default value
        }

# Global configuration instance
unified_config = ConfigManager()

# Legacy compatibility
def get_config_value(section: str, key: str, default=None, value_type=str):
    """Legacy compatibility function"""
    return unified_config.get_legacy_config_value(section, key, default, value_type)
