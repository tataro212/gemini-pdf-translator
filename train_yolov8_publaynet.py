"""
Train YOLOv8 on PubLayNet Dataset

This script fine-tunes YOLOv8 on the PubLayNet dataset for supreme accuracy
in document layout analysis.
"""

import os
import logging
import torch
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_yolov8_on_publaynet():
    """Train YOLOv8 model on PubLayNet dataset"""
    
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("❌ ultralytics not installed. Run: pip install ultralytics")
        return
    
    logger.info("🎯 Starting YOLOv8 Fine-tuning on PubLayNet...")
    
    # Configuration with GPU memory optimization
    config = {
        'model_size': 'yolov8m.pt',  # Medium model for balance of speed/accuracy
        'data_config': '../datasets/publaynet_yolo/data_specialized.yaml',  # Use specialized config
        'epochs': 200,  # Increased epochs for better accuracy
        'batch_size': 8,  # Reduced for RTX 3050 Laptop GPU
        'image_size': 640,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'workers': 4,  # Reduced to prevent memory pressure
        'project': 'publaynet_training',
        'name': f'yolov8_specialized_{int(time.time())}',
        
        # Training optimizations
        'optimizer': 'AdamW',  # Better optimizer
        'lr0': 0.01,  # Initial learning rate
        'lrf': 0.001,  # Final learning rate
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,  # Box loss gain
        'cls': 0.5,  # Class loss gain
        'dfl': 1.5,  # DFL loss gain
        'pose': 12.0,  # Pose loss gain
        'kobj': 1.0,  # Keypoint obj loss gain
        'label_smoothing': 0.0,
        'nbs': 64,  # Nominal batch size
        'hsv_h': 0.015,  # Image HSV-Hue augmentation
        'hsv_s': 0.7,  # Image HSV-Saturation augmentation
        'hsv_v': 0.4,  # Image HSV-Value augmentation
        'degrees': 0.0,  # Image rotation (+/- deg)
        'translate': 0.1,  # Image translation (+/- fraction)
        'scale': 0.5,  # Image scale (+/- gain)
        'shear': 0.0,  # Image shear (+/- deg)
        'perspective': 0.0,  # Image perspective (+/- fraction)
        'flipud': 0.0,  # Image flip up-down (probability)
        'fliplr': 0.5,  # Image flip left-right (probability)
        'mosaic': 1.0,  # Image mosaic (probability)
        'mixup': 0.0,  # Image mixup (probability)
        'copy_paste': 0.0,  # Segment copy-paste (probability)
        'auto_augment': 'randaugment',  # Auto augment policy
        'erasing': 0.4,  # Random erasing (probability)
        'crop_fraction': 1.0,  # Fraction of image to crop
        'cache': False,  # Cache images in memory
        'amp': True,  # Automatic Mixed Precision
        'rect': False,  # Rectangular training
        'cos_lr': True,  # Cosine learning rate scheduler
        'close_mosaic': 10,  # Disable mosaic for last epochs
        'resume': False,  # Resume training from last checkpoint
        'patience': 50,  # Early stopping patience
        'save_period': 5,  # Save checkpoint every N epochs
        'local_rank': -1,  # Local rank for distributed training
        'exist_ok': True,  # Overwrite existing experiment
        'pretrained': True,  # Use pretrained model
        'optimizer': 'AdamW',  # Optimizer (SGD, Adam, AdamW, etc.)
        'verbose': True,  # Print verbose output
        'seed': 0,  # Random seed
        'deterministic': True,  # Deterministic training
        'single_cls': False,  # Train as single-class dataset
        'image_weights': False,  # Use weighted image selection
        'multi_scale': False,  # Vary img-size +/- 50%
        'single_cls': False,  # Train as single-class dataset
        'overlap_mask': True,  # Masks should overlap during training
        'mask_ratio': 4,  # Mask downsample ratio
        'dropout': 0.0,  # Use dropout regularization
        'val': True,  # Validate training results
        'save_json': False,  # Save a COCO-JSON results file
        'save_hybrid': False,  # Save hybrid version of labels
        'conf': None,  # Confidence threshold
        'iou': 0.7,  # NMS IoU threshold
        'max_det': 300,  # Maximum detections per image
        'half': False,  # Use FP16 half-precision inference
        'dnn': False,  # Use OpenCV DNN for ONNX inference
        'plots': True,  # Save plots for train/val
        'source': None,  # Source directory for images
        'show': False,  # Show results if possible
        'save_txt': False,  # Save results to *.txt
        'save_conf': False,  # Save confidences in --save-txt labels
        'save_crop': False,  # Save cropped prediction boxes
        'show_labels': True,  # Show labels in plots
        'show_conf': True,  # Show confidences in plots
        'show_boxes': True,  # Show boxes in plots
        'line_width': None,  # Line width of bounding boxes
        'visualize': False,  # Visualize features
        'augment': False,  # Apply augmentations to prediction
        'agnostic_nms': False,  # Class-agnostic NMS
        'classes': None,  # Filter by class
        'retina_masks': False,  # Use high-resolution segmentation masks
        'boxes': True,  # Show boxes in segmentation predictions
        'format': 'torchscript',  # Export format
        'keras': False,  # Use Keras
        'optimize': False,  # TorchScript: optimize for mobile
        'int8': False,  # CoreML/TF INT8 quantization
        'dynamic': False,  # ONNX/TF/TensorRT: dynamic axes
        'simplify': True,  # ONNX: simplify model
        'opset': None,  # ONNX: opset version
        'workspace': None,  # TensorRT: workspace size (GB)
        'nms': False,  # CoreML: add NMS
    }

    # GPU memory optimization
    if config['device'] == 'cuda':
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        if gpu_memory_gb < 6:  # Less than 6GB VRAM
            config['batch_size'] = 4
            config['workers'] = 2
            logger.warning(f"⚠️ Limited GPU memory ({gpu_memory_gb:.1f}GB), reducing batch size to {config['batch_size']}")
        elif gpu_memory_gb < 8:  # Less than 8GB VRAM
            config['batch_size'] = 6
            config['workers'] = 3
    
    # Check if dataset config exists
    if not os.path.exists(config['data_config']):
        logger.error(f"❌ Dataset config not found: {config['data_config']}")
        logger.info("Please run: python convert_publaynet_to_yolo.py first")
        return
    
    # Display configuration
    logger.info("📋 Training Configuration:")
    logger.info(f"   • Model: {config['model_size']}")
    logger.info(f"   • Dataset: {config['data_config']}")
    logger.info(f"   • Epochs: {config['epochs']}")
    logger.info(f"   • Batch size: {config['batch_size']}")
    logger.info(f"   • Device: {config['device']}")
    logger.info(f"   • Image size: {config['image_size']}")
    
    if config['device'] == 'cuda':
        logger.info(f"   • GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"   • GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    try:
        # Load pre-trained YOLOv8 model
        logger.info("📥 Loading pre-trained YOLOv8 model...")
        model = YOLO(config['model_size'])

        # Check for existing checkpoint to resume
        checkpoint_path = f"{config['project']}/{config['name']}/weights/last.pt"
        resume_training = os.path.exists(checkpoint_path)

        if resume_training:
            logger.info(f"🔄 Resuming training from checkpoint: {checkpoint_path}")
            model = YOLO(checkpoint_path)  # Load from checkpoint
        else:
            logger.info("🚀 Starting training from scratch...")

        logger.info("This will take several hours depending on your hardware...")

        # Add signal handling for graceful shutdown
        import signal
        import sys

        def signal_handler(sig, frame):
            logger.info("🛑 Training interrupted by user. Saving checkpoint...")
            # The checkpoint will be automatically saved by YOLO
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        results = model.train(
            data=config['data_config'],
            epochs=config['epochs'],
            imgsz=config['image_size'],
            batch=config['batch_size'],
            device=config['device'],
            workers=config['workers'],
            project=config['project'],
            name=config['name'],
            save=True,
            save_period=5,  # Save checkpoint every 5 epochs (more frequent)
            val=True,
            plots=True,
            verbose=True,
            resume=resume_training,  # Resume from checkpoint if available
            patience=50,  # Early stopping patience
            cache=False,  # Disable caching to save memory
            amp=True,  # Automatic Mixed Precision for memory efficiency
            exist_ok=True,  # Allow overwriting existing runs
            optimizer=config['optimizer'],
            lr0=config['lr0'],
            lrf=config['lrf'],
            momentum=config['momentum'],
            weight_decay=config['weight_decay'],
            warmup_epochs=config['warmup_epochs'],
            warmup_momentum=config['warmup_momentum'],
            warmup_bias_lr=config['warmup_bias_lr'],
            box=config['box'],
            cls=config['cls'],
            dfl=config['dfl'],
            pose=config['pose'],
            kobj=config['kobj'],
            label_smoothing=config['label_smoothing'],
            nbs=config['nbs'],
            hsv_h=config['hsv_h'],
            hsv_s=config['hsv_s'],
            hsv_v=config['hsv_v'],
            degrees=config['degrees'],
            translate=config['translate'],
            scale=config['scale'],
            shear=config['shear'],
            perspective=config['perspective'],
            flipud=config['flipud'],
            fliplr=config['fliplr'],
            mosaic=config['mosaic'],
            mixup=config['mixup'],
            copy_paste=config['copy_paste'],
            auto_augment=config['auto_augment'],
            erasing=config['erasing'],
            crop_fraction=config['crop_fraction'],
            cache=config['cache'],
            amp=config['amp'],
            rect=config['rect'],
            cos_lr=config['cos_lr'],
            close_mosaic=config['close_mosaic'],
            resume=config['resume'],
            patience=config['patience'],
            save_period=config['save_period'],
            local_rank=config['local_rank'],
            exist_ok=config['exist_ok'],
            pretrained=config['pretrained'],
            optimizer=config['optimizer'],
            verbose=config['verbose'],
            seed=config['seed'],
            deterministic=config['deterministic'],
            single_cls=config['single_cls'],
            image_weights=config['image_weights'],
            multi_scale=config['multi_scale'],
            overlap_mask=config['overlap_mask'],
            mask_ratio=config['mask_ratio'],
            dropout=config['dropout'],
            val=config['val'],
            save_json=config['save_json'],
            save_hybrid=config['save_hybrid'],
            conf=config['conf'],
            iou=config['iou'],
            max_det=config['max_det'],
            half=config['half'],
            dnn=config['dnn'],
            plots=config['plots'],
            source=config['source'],
            show=config['show'],
            save_txt=config['save_txt'],
            save_conf=config['save_conf'],
            save_crop=config['save_crop'],
            show_labels=config['show_labels'],
            show_conf=config['show_conf'],
            show_boxes=config['show_boxes'],
            line_width=config['line_width'],
            visualize=config['visualize'],
            augment=config['augment'],
            agnostic_nms=config['agnostic_nms'],
            classes=config['classes'],
            retina_masks=config['retina_masks'],
            boxes=config['boxes'],
            format=config['format'],
            keras=config['keras'],
            optimize=config['optimize'],
            int8=config['int8'],
            dynamic=config['dynamic'],
            simplify=config['simplify'],
            opset=config['opset'],
            workspace=config['workspace'],
            nms=config['nms']
        )
        
        logger.info("✅ Training completed successfully!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return None

def validate_trained_model(model_path):
    """Validate the trained model"""
    
    try:
        from ultralytics import YOLO
        
        logger.info("🔍 Validating trained model...")
        
        # Load trained model
        model = YOLO(model_path)
        
        # Run validation (PublayNet doesn't have test split, use val)
        results = model.val(
            data='../datasets/publaynet_yolo/publaynet.yaml',
            split='val',
            save_json=True,
            save_hybrid=True
        )
        
        logger.info("✅ Validation completed!")
        logger.info(f"📊 Test mAP50: {results.box.map50}")
        logger.info(f"📊 Test mAP50-95: {results.box.map}")
        
        # Class-wise performance
        logger.info("📋 Class-wise Performance:")
        class_names = ['text', 'title', 'list', 'table', 'figure']
        for i, class_name in enumerate(class_names):
            if i < len(results.box.ap50):
                logger.info(f"   • {class_name}: mAP50 = {results.box.ap50[i]:.3f}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return None

def test_model_inference(model_path):
    """Test the trained model on a sample image"""
    
    try:
        from ultralytics import YOLO
        import glob
        
        logger.info("🧪 Testing model inference...")
        
        # Load trained model
        model = YOLO(model_path)
        
        # Find a validation image (since PublayNet doesn't have test split)
        val_images = glob.glob("../datasets/publaynet_yolo/images/val/*.jpg")
        if not val_images:
            logger.warning("No validation images found for inference test")
            return

        test_image = val_images[0]
        logger.info(f"Testing on: {os.path.basename(test_image)}")
        
        # Run inference
        results = model(test_image)
        
        # Display results
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                logger.info(f"Detected {len(boxes)} objects:")
                class_names = ['text', 'title', 'list', 'table', 'figure']
                for box in boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    class_name = class_names[class_id] if class_id < len(class_names) else 'unknown'
                    logger.info(f"   • {class_name}: {confidence:.3f}")
        
        # Save result image
        result_path = "test_inference_result.jpg"
        results[0].save(result_path)
        logger.info(f"📸 Result saved to: {result_path}")
        
    except Exception as e:
        logger.error(f"❌ Inference test failed: {e}")

def main():
    """Main training function"""
    
    logger.info("🎯 YOLOv8 PubLayNet Fine-tuning Pipeline")
    logger.info("=" * 50)
    
    # Check prerequisites
    logger.info("🔍 Checking prerequisites...")
    
    # Check if dataset is ready
    if not os.path.exists("../datasets/publaynet_yolo/publaynet.yaml"):
        logger.error("❌ PubLayNet dataset not prepared for YOLOv8")
        logger.info("Please run: python convert_publaynet_to_yolo.py first")
        return
    
    # Check GPU availability
    if torch.cuda.is_available():
        logger.info(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
    else:
        logger.warning("⚠️ No GPU available - training will be slow on CPU")
        response = input("Continue with CPU training? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Start training
    results = train_yolov8_on_publaynet()
    
    if results:
        # Validate the trained model
        validate_trained_model(results.model.model[-1].path)
        
        # Test inference
        test_model_inference(results.model.model[-1].path)
        
        logger.info("🎉 YOLOv8 fine-tuning pipeline completed!")
        logger.info(f"🎯 Your supreme accuracy model is ready: {results.model.model[-1].path}")
        logger.info("\nNext steps:")
        logger.info("1. Update yolov8_service.py to use your fine-tuned model")
        logger.info("2. Start the service: python yolov8_service.py")
        logger.info("3. Test the integration: python test_yolov8_integration.py")
    else:
        logger.error("❌ Training failed - please check the logs above")

if __name__ == "__main__":
    main()
