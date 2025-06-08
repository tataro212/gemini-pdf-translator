"""
ONNX-based Image Classifier for Ultimate PDF Translator

Implements lightweight image pre-filtering using ONNX Runtime with MobileNetV2
to reduce API calls by automatically discarding irrelevant images.

Features:
- Local MobileNetV2 classification to avoid API costs
- Automatic detection of decorative content
- Relevance scoring for images
- Smart filtering to reduce unnecessary processing
"""

import os
import logging
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from PIL import Image
import numpy as np

# Optional imports for enhanced functionality
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("ONNX Runtime not available - using basic image classification")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests not available - cannot download models")

logger = logging.getLogger(__name__)

class ImageCategory(Enum):
    """Image classification categories"""
    DIAGRAM = "diagram"
    CHART = "chart"
    PHOTOGRAPH = "photograph"
    DECORATIVE = "decorative"
    LOGO = "logo"
    TEXT_IMAGE = "text_image"
    TECHNICAL_DRAWING = "technical_drawing"
    UNKNOWN = "unknown"

class RelevanceLevel(Enum):
    """Image relevance levels for processing decisions"""
    HIGH = "high"          # Definitely process
    MEDIUM = "medium"      # Process with lower priority
    LOW = "low"           # Consider skipping
    SKIP = "skip"         # Definitely skip

@dataclass
class ImageClassification:
    """Result of image classification"""
    category: ImageCategory
    relevance: RelevanceLevel
    confidence: float
    reasoning: str
    should_process: bool
    estimated_api_cost: float

class ONNXImageClassifier:
    """Lightweight image classifier using ONNX Runtime and MobileNetV2"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "models/mobilenetv2.onnx"
        self.session = None
        self.input_name = None
        self.output_name = None
        self.class_labels = self._load_imagenet_labels()
        
        # Classification rules for relevance determination
        self.relevance_rules = {
            'high_relevance_keywords': [
                'diagram', 'chart', 'graph', 'plot', 'schematic', 'flowchart',
                'technical', 'blueprint', 'circuit', 'map', 'illustration'
            ],
            'medium_relevance_keywords': [
                'document', 'text', 'page', 'book', 'paper', 'screenshot',
                'table', 'form', 'certificate', 'receipt'
            ],
            'low_relevance_keywords': [
                'person', 'face', 'building', 'landscape', 'food', 'animal',
                'vehicle', 'furniture', 'clothing', 'nature'
            ],
            'skip_keywords': [
                'logo', 'watermark', 'decoration', 'border', 'frame',
                'background', 'texture', 'pattern', 'noise'
            ]
        }
        
        # Initialize model if available
        if ONNX_AVAILABLE:
            self._initialize_model()
        else:
            logger.warning("ONNX Runtime not available - using heuristic classification")
    
    def _initialize_model(self):
        """Initialize ONNX model for image classification"""
        try:
            # Download model if it doesn't exist
            if not os.path.exists(self.model_path):
                self._download_mobilenet_model()
            
            if os.path.exists(self.model_path):
                self.session = ort.InferenceSession(self.model_path)
                self.input_name = self.session.get_inputs()[0].name
                self.output_name = self.session.get_outputs()[0].name
                logger.info(f"✅ MobileNetV2 model loaded: {self.model_path}")
            else:
                logger.warning("MobileNetV2 model not found - using heuristic classification")
                
        except Exception as e:
            logger.error(f"Failed to initialize ONNX model: {e}")
            self.session = None
    
    def _download_mobilenet_model(self):
        """Download MobileNetV2 ONNX model if not present"""
        if not REQUESTS_AVAILABLE:
            logger.warning("Cannot download model - requests library not available")
            return

        # Try multiple model URLs
        model_urls = [
            "https://github.com/onnx/models/raw/main/vision/classification/mobilenet/model/mobilenetv2-12.onnx",
            "https://github.com/onnx/models/raw/main/vision/classification/mobilenet/model/mobilenetv2-10.onnx",
            "https://github.com/onnx/models/raw/main/vision/classification/mobilenet/model/mobilenetv2-7.onnx"
        ]
        
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            # Try each URL until one works
            for model_url in model_urls:
                try:
                    logger.info(f"📥 Trying to download MobileNetV2 model from: {model_url}")
                    response = requests.get(model_url, stream=True)
                    response.raise_for_status()

                    with open(self.model_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    logger.info(f"✅ Model downloaded successfully: {self.model_path}")
                    return  # Success, exit the function

                except Exception as e:
                    logger.warning(f"Failed to download from {model_url}: {e}")
                    continue

            # If we get here, all URLs failed
            logger.error("Failed to download model from any URL - using heuristic classification only")

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
    
    def _load_imagenet_labels(self) -> List[str]:
        """Load ImageNet class labels"""
        # Simplified ImageNet labels for common categories
        return [
            'background', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
            'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
            'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
            'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat',
            'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
            'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
            'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
            'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
    
    def classify_image(self, image_path: str) -> ImageClassification:
        """Classify an image and determine its processing relevance"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            # Get classification using ONNX model or heuristics
            if self.session:
                category, confidence = self._classify_with_onnx(image)
            else:
                category, confidence = self._classify_with_heuristics(image_path, image)
            
            # Determine relevance based on category
            relevance = self._determine_relevance(category, confidence)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(category, relevance, confidence)
            
            # Decide whether to process
            should_process = relevance in [RelevanceLevel.HIGH, RelevanceLevel.MEDIUM]
            
            # Estimate API cost if processed
            estimated_cost = self._estimate_api_cost(image, relevance)
            
            return ImageClassification(
                category=category,
                relevance=relevance,
                confidence=confidence,
                reasoning=reasoning,
                should_process=should_process,
                estimated_api_cost=estimated_cost
            )
            
        except Exception as e:
            logger.error(f"Image classification failed for {image_path}: {e}")
            # Return safe default
            return ImageClassification(
                category=ImageCategory.UNKNOWN,
                relevance=RelevanceLevel.MEDIUM,
                confidence=0.5,
                reasoning=f"Classification failed: {e}",
                should_process=True,
                estimated_api_cost=0.002
            )
    
    def _classify_with_onnx(self, image: Image.Image) -> Tuple[ImageCategory, float]:
        """Classify image using ONNX MobileNetV2 model"""
        try:
            # Preprocess image for MobileNetV2
            image_array = self._preprocess_image(image)
            
            # Run inference
            outputs = self.session.run([self.output_name], {self.input_name: image_array})
            predictions = outputs[0][0]
            
            # Get top prediction
            top_class_idx = np.argmax(predictions)
            confidence = float(predictions[top_class_idx])
            
            # Map to our categories
            if top_class_idx < len(self.class_labels):
                class_name = self.class_labels[top_class_idx]
                category = self._map_to_category(class_name)
            else:
                category = ImageCategory.UNKNOWN
            
            return category, confidence
            
        except Exception as e:
            logger.error(f"ONNX classification failed: {e}")
            return ImageCategory.UNKNOWN, 0.5
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for MobileNetV2 input"""
        # Resize to 224x224 (MobileNetV2 input size)
        image = image.resize((224, 224))
        
        # Convert to numpy array and normalize
        image_array = np.array(image).astype(np.float32)
        image_array = image_array / 255.0  # Normalize to [0, 1]
        
        # Normalize with ImageNet mean and std
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_array = (image_array - mean) / std
        
        # Add batch dimension and transpose to NCHW format
        image_array = np.transpose(image_array, (2, 0, 1))
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def _classify_with_heuristics(self, image_path: str, image: Image.Image) -> Tuple[ImageCategory, float]:
        """Classify image using heuristic methods when ONNX is not available"""
        filename = os.path.basename(image_path).lower()
        
        # Check filename for clues
        if any(word in filename for word in ['logo', 'watermark', 'decoration']):
            return ImageCategory.DECORATIVE, 0.8
        
        if any(word in filename for word in ['diagram', 'chart', 'graph', 'plot']):
            return ImageCategory.DIAGRAM, 0.7
        
        if any(word in filename for word in ['photo', 'picture', 'img']):
            return ImageCategory.PHOTOGRAPH, 0.6
        
        # Analyze image properties
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1.0
        
        # Very wide or tall images might be decorative
        if aspect_ratio > 5.0 or aspect_ratio < 0.2:
            return ImageCategory.DECORATIVE, 0.6
        
        # Small images are often logos or decorative
        if width < 100 or height < 100:
            return ImageCategory.LOGO, 0.7
        
        # Default to unknown with medium confidence
        return ImageCategory.UNKNOWN, 0.5

    def _map_to_category(self, class_name: str) -> ImageCategory:
        """Map ImageNet class name to our categories"""
        class_name = class_name.lower()

        # Technical/diagram content
        if any(word in class_name for word in ['computer', 'laptop', 'monitor', 'screen']):
            return ImageCategory.TECHNICAL_DRAWING

        # Charts and graphs (limited in ImageNet)
        if any(word in class_name for word in ['book', 'paper', 'document']):
            return ImageCategory.TEXT_IMAGE

        # Decorative items
        if any(word in class_name for word in ['vase', 'decoration', 'frame', 'clock']):
            return ImageCategory.DECORATIVE

        # People and general photos
        if any(word in class_name for word in ['person', 'face', 'people']):
            return ImageCategory.PHOTOGRAPH

        # Default mapping
        return ImageCategory.UNKNOWN

    def _determine_relevance(self, category: ImageCategory, confidence: float) -> RelevanceLevel:
        """Determine processing relevance based on category and confidence"""

        # High relevance categories
        if category in [ImageCategory.DIAGRAM, ImageCategory.CHART, ImageCategory.TECHNICAL_DRAWING]:
            return RelevanceLevel.HIGH if confidence > 0.6 else RelevanceLevel.MEDIUM

        # Medium relevance categories
        if category == ImageCategory.TEXT_IMAGE:
            return RelevanceLevel.MEDIUM if confidence > 0.5 else RelevanceLevel.LOW

        # Low relevance categories
        if category == ImageCategory.PHOTOGRAPH:
            return RelevanceLevel.LOW if confidence > 0.7 else RelevanceLevel.SKIP

        # Skip decorative content
        if category in [ImageCategory.DECORATIVE, ImageCategory.LOGO]:
            return RelevanceLevel.SKIP

        # Unknown content - be conservative
        if category == ImageCategory.UNKNOWN:
            return RelevanceLevel.MEDIUM if confidence > 0.6 else RelevanceLevel.LOW

        return RelevanceLevel.MEDIUM

    def _generate_reasoning(self, category: ImageCategory, relevance: RelevanceLevel, confidence: float) -> str:
        """Generate human-readable reasoning for the classification"""
        reasoning_map = {
            (ImageCategory.DIAGRAM, RelevanceLevel.HIGH): f"Detected diagram/technical content (confidence: {confidence:.2f}) - likely important for translation",
            (ImageCategory.CHART, RelevanceLevel.HIGH): f"Detected chart/graph (confidence: {confidence:.2f}) - contains data visualization",
            (ImageCategory.TECHNICAL_DRAWING, RelevanceLevel.HIGH): f"Detected technical drawing (confidence: {confidence:.2f}) - specialized content",
            (ImageCategory.TEXT_IMAGE, RelevanceLevel.MEDIUM): f"Detected text in image (confidence: {confidence:.2f}) - may need OCR",
            (ImageCategory.PHOTOGRAPH, RelevanceLevel.LOW): f"Detected photograph (confidence: {confidence:.2f}) - likely not essential for translation",
            (ImageCategory.DECORATIVE, RelevanceLevel.SKIP): f"Detected decorative content (confidence: {confidence:.2f}) - can be safely skipped",
            (ImageCategory.LOGO, RelevanceLevel.SKIP): f"Detected logo/branding (confidence: {confidence:.2f}) - not relevant for translation",
            (ImageCategory.UNKNOWN, RelevanceLevel.MEDIUM): f"Unknown content type (confidence: {confidence:.2f}) - processing recommended for safety"
        }

        key = (category, relevance)
        return reasoning_map.get(key, f"Category: {category.value}, Relevance: {relevance.value} (confidence: {confidence:.2f})")

    def _estimate_api_cost(self, image: Image.Image, relevance: RelevanceLevel) -> float:
        """Estimate API cost for processing this image"""
        # Base cost for vision API (approximate)
        base_cost = 0.002  # $0.002 per image

        # Adjust based on image size
        width, height = image.size
        pixel_count = width * height

        if pixel_count > 1000000:  # Large images cost more
            size_multiplier = 1.5
        elif pixel_count < 100000:  # Small images cost less
            size_multiplier = 0.7
        else:
            size_multiplier = 1.0

        # Adjust based on relevance (high relevance might use more expensive models)
        relevance_multiplier = {
            RelevanceLevel.HIGH: 1.2,
            RelevanceLevel.MEDIUM: 1.0,
            RelevanceLevel.LOW: 0.8,
            RelevanceLevel.SKIP: 0.0
        }.get(relevance, 1.0)

        return base_cost * size_multiplier * relevance_multiplier

    def filter_images_batch(self, image_paths: List[str]) -> Dict[str, ImageClassification]:
        """Filter a batch of images and return classifications"""
        logger.info(f"🔍 Classifying {len(image_paths)} images...")

        classifications = {}
        processed_count = 0
        skipped_count = 0

        for image_path in image_paths:
            try:
                classification = self.classify_image(image_path)
                classifications[image_path] = classification

                if classification.should_process:
                    processed_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                logger.error(f"Failed to classify {image_path}: {e}")
                # Add default classification for failed images
                classifications[image_path] = ImageClassification(
                    category=ImageCategory.UNKNOWN,
                    relevance=RelevanceLevel.MEDIUM,
                    confidence=0.5,
                    reasoning=f"Classification failed: {e}",
                    should_process=True,
                    estimated_api_cost=0.002
                )
                processed_count += 1

        logger.info(f"✅ Classification complete: {processed_count} to process, {skipped_count} to skip")
        return classifications

    def get_processing_summary(self, classifications: Dict[str, ImageClassification]) -> Dict:
        """Generate a summary of processing recommendations"""
        if not classifications:
            return {}

        total_images = len(classifications)
        to_process = sum(1 for c in classifications.values() if c.should_process)
        to_skip = total_images - to_process

        total_cost = sum(c.estimated_api_cost for c in classifications.values() if c.should_process)

        category_counts = {}
        relevance_counts = {}

        for classification in classifications.values():
            category = classification.category.value
            relevance = classification.relevance.value

            category_counts[category] = category_counts.get(category, 0) + 1
            relevance_counts[relevance] = relevance_counts.get(relevance, 0) + 1

        return {
            'total_images': total_images,
            'to_process': to_process,
            'to_skip': to_skip,
            'skip_percentage': (to_skip / total_images) * 100 if total_images > 0 else 0,
            'estimated_total_cost': total_cost,
            'cost_savings': (to_skip * 0.002),  # Estimated savings from skipped images
            'category_distribution': category_counts,
            'relevance_distribution': relevance_counts
        }

# Factory function for easy instantiation
def create_image_classifier(model_path: Optional[str] = None) -> ONNXImageClassifier:
    """Create and initialize an ONNX image classifier"""
    return ONNXImageClassifier(model_path)

# Convenience function for batch processing
def filter_images_for_processing(image_paths: List[str], model_path: Optional[str] = None) -> Tuple[List[str], Dict]:
    """Filter images and return list of images to process plus summary"""
    classifier = create_image_classifier(model_path)
    classifications = classifier.filter_images_batch(image_paths)

    # Get images that should be processed
    images_to_process = [
        path for path, classification in classifications.items()
        if classification.should_process
    ]

    # Get summary
    summary = classifier.get_processing_summary(classifications)

    return images_to_process, summary
