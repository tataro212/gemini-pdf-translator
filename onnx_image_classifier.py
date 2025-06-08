#!/usr/bin/env python3
"""
ONNX Image Classifier
Provides intelligent image classification for translation relevance using ONNX Runtime
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import hashlib

# Optional imports for enhanced functionality
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class RelevanceLevel(Enum):
    """Image relevance levels for translation"""
    HIGH = "high"          # Important diagrams, charts, text-heavy images
    MEDIUM = "medium"      # Moderate importance, some text content
    LOW = "low"           # Decorative images, simple graphics
    SKIP = "skip"         # Irrelevant images, logos, watermarks

@dataclass
class ImageClassification:
    """Image classification result"""
    relevance: RelevanceLevel
    confidence: float
    reasoning: str
    detected_features: List[str]
    text_likelihood: float
    processing_recommendation: str

class ONNXImageClassifier:
    """
    ONNX-based image classifier for determining translation relevance
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.output_names = None
        self.classification_cache = {}
        
        # Feature detection patterns
        self.feature_patterns = {
            'text_indicators': [
                'high_contrast_regions',
                'horizontal_lines',
                'regular_spacing',
                'character_like_shapes'
            ],
            'diagram_indicators': [
                'geometric_shapes',
                'connecting_lines',
                'structured_layout',
                'arrows_or_connectors'
            ],
            'chart_indicators': [
                'grid_patterns',
                'axis_like_structures',
                'data_visualization_elements',
                'legend_areas'
            ],
            'decorative_indicators': [
                'artistic_elements',
                'irregular_patterns',
                'color_gradients',
                'photographic_content'
            ]
        }
        
        # Initialize ONNX session if available
        if ONNX_AVAILABLE and PIL_AVAILABLE:
            self._initialize_onnx_session()
        else:
            logger.warning("ONNX Runtime or PIL not available, using heuristic classification")
    
    def _initialize_onnx_session(self):
        """Initialize ONNX Runtime session"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                # Load custom model
                self.session = ort.InferenceSession(self.model_path)
                self.input_name = self.session.get_inputs()[0].name
                self.output_names = [output.name for output in self.session.get_outputs()]
                logger.info(f"✅ ONNX model loaded: {self.model_path}")
            else:
                # Use built-in heuristic classification
                logger.info("🔧 Using heuristic image classification (no ONNX model)")
                
        except Exception as e:
            logger.warning(f"Failed to initialize ONNX session: {e}")
            self.session = None
    
    def classify_image(self, image_path: str) -> ImageClassification:
        """
        Classify image for translation relevance
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ImageClassification with relevance assessment
        """
        # Check cache first
        cache_key = self._get_cache_key(image_path)
        if cache_key in self.classification_cache:
            return self.classification_cache[cache_key]
        
        try:
            if self.session and ONNX_AVAILABLE and PIL_AVAILABLE:
                classification = self._classify_with_onnx(image_path)
            else:
                classification = self._classify_heuristic(image_path)
            
            # Cache the result
            self.classification_cache[cache_key] = classification
            
            logger.debug(f"Image classified: {os.path.basename(image_path)} -> {classification.relevance.value}")
            return classification
            
        except Exception as e:
            logger.error(f"Image classification failed for {image_path}: {e}")
            return ImageClassification(
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.5,
                reasoning=f"Classification failed: {e}",
                detected_features=[],
                text_likelihood=0.5,
                processing_recommendation="standard"
            )
    
    def _classify_with_onnx(self, image_path: str) -> ImageClassification:
        """Classify image using ONNX model"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            input_tensor = self._preprocess_image(image)
            
            # Run inference
            outputs = self.session.run(self.output_names, {self.input_name: input_tensor})
            
            # Process outputs (this would depend on your specific model)
            # For now, using heuristic as fallback
            return self._classify_heuristic(image_path)
            
        except Exception as e:
            logger.warning(f"ONNX classification failed: {e}, falling back to heuristic")
            return self._classify_heuristic(image_path)
    
    def _classify_heuristic(self, image_path: str) -> ImageClassification:
        """Classify image using heuristic analysis"""
        try:
            if not PIL_AVAILABLE:
                return self._classify_by_filename(image_path)
            
            # Load image for analysis
            image = Image.open(image_path)
            width, height = image.size
            
            # Basic image analysis
            features = self._analyze_image_features(image)
            
            # Determine relevance based on features
            relevance, confidence, reasoning = self._determine_relevance(features, width, height)
            
            # Calculate text likelihood
            text_likelihood = self._estimate_text_likelihood(features)
            
            # Generate processing recommendation
            processing_rec = self._recommend_processing(relevance, features)
            
            return ImageClassification(
                relevance=relevance,
                confidence=confidence,
                reasoning=reasoning,
                detected_features=features,
                text_likelihood=text_likelihood,
                processing_recommendation=processing_rec
            )
            
        except Exception as e:
            logger.warning(f"Heuristic classification failed: {e}")
            return self._classify_by_filename(image_path)
    
    def _analyze_image_features(self, image: Image.Image) -> List[str]:
        """Analyze image features for classification"""
        features = []
        
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Basic feature detection
            if len(img_array.shape) == 3:
                # Color image analysis
                gray = np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            # Detect high contrast regions (potential text)
            contrast = np.std(gray)
            if contrast > 50:
                features.append('high_contrast_regions')
            
            # Detect horizontal/vertical structures
            if self._has_linear_structures(gray):
                features.append('structured_layout')
            
            # Detect regular patterns (potential text or diagrams)
            if self._has_regular_patterns(gray):
                features.append('regular_spacing')
            
            # Analyze aspect ratio
            height, width = gray.shape
            aspect_ratio = width / height
            
            if 0.5 < aspect_ratio < 2.0:
                features.append('document_like_aspect')
            
            # Detect edges (potential diagrams/charts)
            edge_density = self._calculate_edge_density(gray)
            if edge_density > 0.1:
                features.append('geometric_shapes')
            
        except Exception as e:
            logger.warning(f"Feature analysis failed: {e}")
            features.append('analysis_failed')
        
        return features
    
    def _has_linear_structures(self, gray_image: np.ndarray) -> bool:
        """Detect linear structures in image"""
        try:
            # Simple edge detection
            edges_h = np.abs(np.diff(gray_image, axis=0))
            edges_v = np.abs(np.diff(gray_image, axis=1))
            
            # Check for strong horizontal/vertical lines
            strong_h_lines = np.sum(edges_h > 30) / edges_h.size
            strong_v_lines = np.sum(edges_v > 30) / edges_v.size
            
            return strong_h_lines > 0.01 or strong_v_lines > 0.01
        except:
            return False
    
    def _has_regular_patterns(self, gray_image: np.ndarray) -> bool:
        """Detect regular patterns that might indicate text or structured content"""
        try:
            # Simple pattern detection using variance in small windows
            h, w = gray_image.shape
            window_size = min(20, h // 10, w // 10)
            
            if window_size < 5:
                return False
            
            variances = []
            for i in range(0, h - window_size, window_size):
                for j in range(0, w - window_size, window_size):
                    window = gray_image[i:i+window_size, j:j+window_size]
                    variances.append(np.var(window))
            
            # Regular patterns have consistent variance
            if len(variances) > 4:
                variance_std = np.std(variances)
                return variance_std < np.mean(variances) * 0.5
            
            return False
        except:
            return False
    
    def _calculate_edge_density(self, gray_image: np.ndarray) -> float:
        """Calculate edge density in image"""
        try:
            # Simple edge detection
            edges_h = np.abs(np.diff(gray_image, axis=0))
            edges_v = np.abs(np.diff(gray_image, axis=1))
            
            # Count strong edges
            strong_edges = np.sum(edges_h > 20) + np.sum(edges_v > 20)
            total_pixels = gray_image.size
            
            return strong_edges / total_pixels
        except:
            return 0.0
    
    def _determine_relevance(self, features: List[str], width: int, height: int) -> Tuple[RelevanceLevel, float, str]:
        """Determine relevance level based on features"""
        
        # High relevance indicators
        high_indicators = [
            'high_contrast_regions',
            'structured_layout',
            'regular_spacing',
            'document_like_aspect'
        ]
        
        # Medium relevance indicators
        medium_indicators = [
            'geometric_shapes',
            'connecting_lines'
        ]
        
        # Low relevance indicators
        low_indicators = [
            'artistic_elements',
            'color_gradients',
            'photographic_content'
        ]
        
        high_score = sum(1 for feature in features if feature in high_indicators)
        medium_score = sum(1 for feature in features if feature in medium_indicators)
        low_score = sum(1 for feature in features if feature in low_indicators)
        
        # Size considerations
        pixel_count = width * height
        
        # Very small images are likely decorative
        if pixel_count < 10000:  # Less than 100x100
            return RelevanceLevel.LOW, 0.7, "Small decorative image"
        
        # Very large images might be full-page scans
        if pixel_count > 2000000:  # Larger than ~1400x1400
            return RelevanceLevel.HIGH, 0.8, "Large document scan"
        
        # Determine relevance based on scores
        if high_score >= 2:
            return RelevanceLevel.HIGH, 0.8, f"Text/diagram indicators: {high_score}"
        elif high_score >= 1 or medium_score >= 2:
            return RelevanceLevel.MEDIUM, 0.6, f"Moderate content indicators"
        elif low_score >= 2:
            return RelevanceLevel.LOW, 0.7, f"Decorative content indicators"
        else:
            return RelevanceLevel.MEDIUM, 0.5, "Uncertain classification"
    
    def _estimate_text_likelihood(self, features: List[str]) -> float:
        """Estimate likelihood that image contains text"""
        text_features = [
            'high_contrast_regions',
            'regular_spacing',
            'structured_layout',
            'document_like_aspect'
        ]
        
        text_score = sum(1 for feature in features if feature in text_features)
        return min(1.0, text_score * 0.25)
    
    def _recommend_processing(self, relevance: RelevanceLevel, features: List[str]) -> str:
        """Recommend processing approach for image"""
        
        if relevance == RelevanceLevel.SKIP:
            return "skip"
        elif relevance == RelevanceLevel.HIGH:
            if 'high_contrast_regions' in features:
                return "ocr_priority"
            else:
                return "enhanced_processing"
        elif relevance == RelevanceLevel.MEDIUM:
            return "standard_processing"
        else:
            return "minimal_processing"
    
    def _classify_by_filename(self, image_path: str) -> ImageClassification:
        """Fallback classification based on filename patterns"""
        filename = os.path.basename(image_path).lower()
        
        # Skip patterns
        skip_patterns = ['logo', 'watermark', 'decoration', 'banner', 'header', 'footer']
        if any(pattern in filename for pattern in skip_patterns):
            return ImageClassification(
                relevance=RelevanceLevel.SKIP,
                confidence=0.8,
                reasoning="Filename indicates decorative content",
                detected_features=['filename_analysis'],
                text_likelihood=0.1,
                processing_recommendation="skip"
            )
        
        # High relevance patterns
        high_patterns = ['diagram', 'chart', 'graph', 'table', 'equation', 'formula']
        if any(pattern in filename for pattern in high_patterns):
            return ImageClassification(
                relevance=RelevanceLevel.HIGH,
                confidence=0.7,
                reasoning="Filename indicates important content",
                detected_features=['filename_analysis'],
                text_likelihood=0.7,
                processing_recommendation="enhanced_processing"
            )
        
        # Default to medium relevance
        return ImageClassification(
            relevance=RelevanceLevel.MEDIUM,
            confidence=0.5,
            reasoning="Default classification",
            detected_features=['filename_analysis'],
            text_likelihood=0.5,
            processing_recommendation="standard_processing"
        )
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for ONNX model input"""
        # This would depend on your specific model requirements
        # Common preprocessing: resize, normalize, etc.
        
        # Resize to model input size (example: 224x224)
        image = image.resize((224, 224))
        
        # Convert to numpy array and normalize
        img_array = np.array(image).astype(np.float32) / 255.0
        
        # Add batch dimension and rearrange channels if needed
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def _get_cache_key(self, image_path: str) -> str:
        """Generate cache key for image"""
        try:
            # Use file path and modification time for cache key
            stat = os.stat(image_path)
            content = f"{image_path}_{stat.st_mtime}_{stat.st_size}"
            return hashlib.md5(content.encode()).hexdigest()
        except:
            return hashlib.md5(image_path.encode()).hexdigest()
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics"""
        if not self.classification_cache:
            return {}
        
        relevance_counts = {}
        for classification in self.classification_cache.values():
            relevance = classification.relevance.value
            relevance_counts[relevance] = relevance_counts.get(relevance, 0) + 1
        
        return {
            'total_classified': len(self.classification_cache),
            'relevance_distribution': relevance_counts,
            'average_confidence': sum(c.confidence for c in self.classification_cache.values()) / len(self.classification_cache),
            'cache_size': len(self.classification_cache)
        }

def filter_images_for_processing(image_list: List[Dict], classifier: Optional[ONNXImageClassifier] = None) -> List[Dict]:
    """
    Filter images based on classification results
    
    Args:
        image_list: List of image dictionaries with 'filepath' key
        classifier: Optional classifier instance
        
    Returns:
        Filtered list of images for processing
    """
    if not classifier:
        classifier = ONNXImageClassifier()
    
    filtered_images = []
    
    for image_item in image_list:
        image_path = image_item.get('filepath', '')
        
        if not image_path or not os.path.exists(image_path):
            continue
        
        classification = classifier.classify_image(image_path)
        
        # Add classification info to image item
        image_item['classification'] = classification
        image_item['relevance'] = classification.relevance.value
        image_item['processing_recommendation'] = classification.processing_recommendation
        
        # Filter based on relevance
        if classification.relevance != RelevanceLevel.SKIP:
            filtered_images.append(image_item)
        else:
            logger.info(f"Skipping image {os.path.basename(image_path)}: {classification.reasoning}")
    
    logger.info(f"Image filtering: {len(image_list)} -> {len(filtered_images)} images")
    return filtered_images

def create_image_classifier(model_path: Optional[str] = None) -> ONNXImageClassifier:
    """Create and return an image classifier instance"""
    return ONNXImageClassifier(model_path)

def main():
    """Test the ONNX image classifier"""
    print("🖼️ ONNX Image Classifier Test")
    
    classifier = ONNXImageClassifier()
    
    # Test with sample images if available
    test_images = ["test_image.jpg", "test_diagram.png", "test_chart.gif"]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            classification = classifier.classify_image(image_path)
            print(f"{image_path}: {classification.relevance.value} ({classification.confidence:.2f})")
            print(f"  Reasoning: {classification.reasoning}")
        else:
            print(f"{image_path}: File not found")
    
    # Test filtering
    sample_images = [{'filepath': img} for img in test_images if os.path.exists(img)]
    if sample_images:
        filtered = filter_images_for_processing(sample_images, classifier)
        print(f"Filtered {len(sample_images)} -> {len(filtered)} images")
    
    print("✅ ONNX image classifier test completed")

if __name__ == "__main__":
    main()
