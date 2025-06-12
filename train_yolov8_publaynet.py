"""
Train YOLOv8 on PubLayNet Dataset

This script fine-tunes YOLOv8 on the PubLayNet dataset for supreme accuracy
in document layout analysis.
"""

import os
import logging
import torch
from pathlib import Path

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
        'data_config': '../datasets/publaynet_yolo/publaynet.yaml',
        'epochs': 100,
        'batch_size': 8,  # Reduced for RTX 3050 Laptop GPU
        'image_size': 640,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'workers': 4,  # Reduced to prevent memory pressure
        'project': 'publaynet_training',
        'name': f'yolov8_publaynet_finetuned{len([d for d in os.listdir("publaynet_training") if d.startswith("yolov8_publaynet_finetuned")]) + 1 if os.path.exists("publaynet_training") else ""}'
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
            exist_ok=True  # Allow overwriting existing runs
        )

        # Save the final model
        model_save_path = f"models/yolov8_publaynet_finetuned.pt"
        os.makedirs("models", exist_ok=True)
        model.save(model_save_path)

        logger.info("✅ Training completed successfully!")
        logger.info(f"📁 Model saved to: {model_save_path}")
        logger.info(f"📊 Training results: {config['project']}/{config['name']}")

        # Display training summary
        logger.info("📈 Training Summary:")
        logger.info(f"   • Final mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
        logger.info(f"   • Final mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")

        return model_save_path

    except torch.cuda.OutOfMemoryError as e:
        logger.error("❌ GPU out of memory! Try reducing batch size or image size")
        logger.error(f"Current batch size: {config['batch_size']}, try batch_size=2 or 4")
        return None
    except KeyboardInterrupt:
        logger.info("🛑 Training interrupted by user")
        return None
        
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
    model_path = train_yolov8_on_publaynet()
    
    if model_path:
        # Validate the trained model
        validate_trained_model(model_path)
        
        # Test inference
        test_model_inference(model_path)
        
        logger.info("🎉 YOLOv8 fine-tuning pipeline completed!")
        logger.info(f"🎯 Your supreme accuracy model is ready: {model_path}")
        logger.info("\nNext steps:")
        logger.info("1. Update yolov8_service.py to use your fine-tuned model")
        logger.info("2. Start the service: python yolov8_service.py")
        logger.info("3. Test the integration: python test_yolov8_integration.py")
    else:
        logger.error("❌ Training failed - please check the logs above")

if __name__ == "__main__":
    main()
