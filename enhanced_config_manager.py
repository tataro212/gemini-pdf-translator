#!/usr/bin/env python3
"""
Enhanced Configuration Manager
Provides advanced configuration management with validation and type safety
"""

import os
import json
import configparser
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass

@dataclass
class ConfigField:
    """Configuration field definition with validation"""
    name: str
    field_type: Type
    default: Any = None
    required: bool = False
    description: str = ""
    choices: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    
    def validate(self, value: Any) -> Any:
        """Validate and convert value"""
        if value is None:
            if self.required:
                raise ConfigValidationError(f"Required field '{self.name}' is missing")
            return self.default
        
        # Type conversion
        try:
            if self.field_type == bool and isinstance(value, str):
                # Handle string boolean values
                value = value.lower() in ('true', '1', 'yes', 'on')
            else:
                value = self.field_type(value)
        except (ValueError, TypeError) as e:
            raise ConfigValidationError(f"Field '{self.name}': Cannot convert '{value}' to {self.field_type.__name__}: {e}")
        
        # Choices validation
        if self.choices and value not in self.choices:
            raise ConfigValidationError(f"Field '{self.name}': Value '{value}' not in allowed choices {self.choices}")
        
        # Range validation
        if self.min_value is not None and value < self.min_value:
            raise ConfigValidationError(f"Field '{self.name}': Value {value} below minimum {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ConfigValidationError(f"Field '{self.name}': Value {value} above maximum {self.max_value}")
        
        return value

@dataclass
class ConfigSection:
    """Configuration section with multiple fields"""
    name: str
    fields: Dict[str, ConfigField] = field(default_factory=dict)
    description: str = ""
    
    def add_field(self, field: ConfigField):
        """Add a field to this section"""
        self.fields[field.name] = field
    
    def validate_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all fields in this section"""
        validated = {}
        
        for field_name, field_def in self.fields.items():
            value = data.get(field_name)
            validated[field_name] = field_def.validate(value)
        
        return validated

class EnhancedConfigManager:
    """Enhanced configuration manager with validation and type safety"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.sections: Dict[str, ConfigSection] = {}
        self.config_data: Dict[str, Dict[str, Any]] = {}
        
        # Define configuration schema
        self._define_schema()
        
        # Load configuration
        self.load_config()
    
    def _define_schema(self):
        """Define the configuration schema with validation rules"""
        
        # Gemini API section
        gemini_section = ConfigSection("GeminiAPI", description="Gemini API configuration")
        gemini_section.add_field(ConfigField(
            "api_key", str, required=True,
            description="Gemini API key from Google AI Studio"
        ))
        gemini_section.add_field(ConfigField(
            "model_name", str, default="models/gemini-1.5-pro",
            choices=["models/gemini-1.5-pro", "models/gemini-1.5-flash", "models/gemini-2.0-flash-exp"],
            description="Gemini model to use"
        ))
        gemini_section.add_field(ConfigField(
            "temperature", float, default=0.1,
            min_value=0.0, max_value=2.0,
            description="Temperature for text generation"
        ))
        gemini_section.add_field(ConfigField(
            "max_tokens", int, default=8192,
            min_value=1, max_value=32768,
            description="Maximum tokens per request"
        ))
        self.sections["GeminiAPI"] = gemini_section
        
        # General section
        general_section = ConfigSection("General", description="General application settings")
        general_section.add_field(ConfigField(
            "target_language", str, default="Greek",
            description="Target language for translation"
        ))
        general_section.add_field(ConfigField(
            "source_language", str, default="auto",
            description="Source language (auto for detection)"
        ))
        general_section.add_field(ConfigField(
            "nougat_only_mode", bool, default=False,
            description="Enable Nougat-only processing mode"
        ))
        general_section.add_field(ConfigField(
            "enable_drive_upload", bool, default=False,
            description="Enable Google Drive upload"
        ))
        general_section.add_field(ConfigField(
            "max_concurrent_translations", int, default=5,
            min_value=1, max_value=20,
            description="Maximum concurrent translation requests"
        ))
        self.sections["General"] = general_section
        
        # Processing section
        processing_section = ConfigSection("Processing", description="Document processing settings")
        processing_section.add_field(ConfigField(
            "enable_footnote_separation", bool, default=True,
            description="Enable AI-powered footnote separation"
        ))
        processing_section.add_field(ConfigField(
            "enable_visual_reconstruction", bool, default=True,
            description="Enable AI-powered visual element reconstruction"
        ))
        processing_section.add_field(ConfigField(
            "quality_threshold", float, default=0.7,
            min_value=0.0, max_value=1.0,
            description="Quality threshold for processing decisions"
        ))
        processing_section.add_field(ConfigField(
            "batch_size", int, default=12000,
            min_value=1000, max_value=50000,
            description="Default batch size for processing"
        ))
        self.sections["Processing"] = processing_section
        
        # Nougat section
        nougat_section = ConfigSection("Nougat", description="Nougat processing configuration")
        nougat_section.add_field(ConfigField(
            "mode", str, default="hybrid",
            choices=["hybrid", "nougat_only", "nougat_first", "disabled"],
            description="Nougat processing mode"
        ))
        nougat_section.add_field(ConfigField(
            "model_version", str, default="0.1.0-base",
            description="Nougat model version"
        ))
        nougat_section.add_field(ConfigField(
            "timeout_seconds", int, default=1200,
            min_value=60, max_value=3600,
            description="Timeout for Nougat processing"
        ))
        nougat_section.add_field(ConfigField(
            "max_retries", int, default=2,
            min_value=0, max_value=5,
            description="Maximum retry attempts"
        ))
        self.sections["Nougat"] = nougat_section
    
    def load_config(self):
        """Load configuration from file with validation"""
        if not self.config_file.exists():
            logger.warning(f"Configuration file {self.config_file} not found, using defaults")
            self._create_default_config()
            return
        
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file, encoding='utf-8')
            
            # Validate and load each section
            for section_name, section_def in self.sections.items():
                if section_name in config:
                    section_data = dict(config[section_name])
                else:
                    section_data = {}
                
                # Validate section
                try:
                    validated_data = section_def.validate_section(section_data)
                    self.config_data[section_name] = validated_data
                    logger.debug(f"Loaded section '{section_name}' with {len(validated_data)} fields")
                except ConfigValidationError as e:
                    logger.error(f"Validation error in section '{section_name}': {e}")
                    # Use defaults for this section
                    default_data = {name: field.default for name, field in section_def.fields.items()}
                    self.config_data[section_name] = default_data
            
            logger.info(f"✅ Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        logger.info("Creating default configuration")
        
        for section_name, section_def in self.sections.items():
            default_data = {}
            for field_name, field_def in section_def.fields.items():
                if field_def.default is not None:
                    default_data[field_name] = field_def.default
            self.config_data[section_name] = default_data
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default"""
        try:
            return self.config_data[section][key]
        except KeyError:
            if default is not None:
                return default
            
            # Try to get default from schema
            if section in self.sections and key in self.sections[section].fields:
                return self.sections[section].fields[key].default
            
            raise KeyError(f"Configuration key '{section}.{key}' not found")
    
    def set_value(self, section: str, key: str, value: Any):
        """Set configuration value with validation"""
        if section not in self.sections:
            raise ConfigValidationError(f"Unknown section '{section}'")
        
        if key not in self.sections[section].fields:
            raise ConfigValidationError(f"Unknown field '{key}' in section '{section}'")
        
        # Validate value
        field_def = self.sections[section].fields[key]
        validated_value = field_def.validate(value)
        
        # Ensure section exists
        if section not in self.config_data:
            self.config_data[section] = {}
        
        self.config_data[section][key] = validated_value
        logger.debug(f"Set {section}.{key} = {validated_value}")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config = configparser.ConfigParser()
            
            for section_name, section_data in self.config_data.items():
                config.add_section(section_name)
                for key, value in section_data.items():
                    config.set(section_name, key, str(value))
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            logger.info(f"✅ Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire section as dictionary"""
        return self.config_data.get(section, {}).copy()
    
    def validate_all(self) -> List[str]:
        """Validate all configuration and return list of errors"""
        errors = []
        
        for section_name, section_def in self.sections.items():
            section_data = self.config_data.get(section_name, {})
            
            try:
                section_def.validate_section(section_data)
            except ConfigValidationError as e:
                errors.append(f"Section '{section_name}': {e}")
        
        return errors
    
    def print_schema(self):
        """Print configuration schema for documentation"""
        print("📋 Configuration Schema")
        print("=" * 50)
        
        for section_name, section_def in self.sections.items():
            print(f"\n[{section_name}]")
            if section_def.description:
                print(f"# {section_def.description}")
            
            for field_name, field_def in section_def.fields.items():
                print(f"# {field_def.description}")
                if field_def.choices:
                    print(f"# Choices: {field_def.choices}")
                if field_def.min_value is not None or field_def.max_value is not None:
                    print(f"# Range: {field_def.min_value} - {field_def.max_value}")
                
                default_str = f" (default: {field_def.default})" if field_def.default is not None else ""
                required_str = " [REQUIRED]" if field_def.required else ""
                print(f"{field_name} = {field_def.default or 'YOUR_VALUE_HERE'}{default_str}{required_str}")
                print()

# Global instance
_config_manager: Optional[EnhancedConfigManager] = None

def get_config_manager(config_file: str = "config.ini") -> EnhancedConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = EnhancedConfigManager(config_file)
    
    return _config_manager

def main():
    """Test the enhanced configuration manager"""
    config = EnhancedConfigManager("test_config.ini")
    
    # Print schema
    config.print_schema()
    
    # Test validation
    errors = config.validate_all()
    if errors:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ All configuration valid")
    
    # Test getting values
    print(f"\nTarget language: {config.get_value('General', 'target_language')}")
    print(f"Nougat mode: {config.get_value('Nougat', 'mode')}")

if __name__ == "__main__":
    main()
