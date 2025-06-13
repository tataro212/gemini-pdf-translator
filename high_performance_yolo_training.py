"""
High-Performance YOLOv8 Training Script
Optimized for maximum GPU utilization and training speed
"""

import os
import logging
import torch
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimize_gpu_settings():
    """Optimize GPU settings for maximum performance"""
    if torch.cuda.is_available():
        # Enable optimizations
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Clear GPU cache
        torch.cuda.empty_cache()
        
        # Get GPU info
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        
        logger.info(f"🚀 GPU Optimization Enabled")
        logger.info(f"   • GPU: {gpu_name}")
        logger.info(f"   • Total Memory: {gpu_memory:.1f} GB")
        logger.info(f"   • CUDNN Benchmark: {torch.backends.cudnn.benchmark}")
        
        return gpu_memory
    else:
        logger.error("❌ No GPU available!")
        return 0

def get_optimal_batch_size(gpu_memory_gb):
    """Calculate optimal batch size based on GPU memory"""
    
    # RTX 3050 Laptop GPU optimized settings
    if gpu_memory_gb >= 4:  # 4GB+ VRAM
        if gpu_memory_gb >= 8:  # 8GB+ VRAM
            return 16, 8  # batch_size, workers
        elif gpu_memory_gb >= 6:  # 6GB+ VRAM  
            return 12, 6  # batch_size, workers
        else:  # 4-6GB VRAM (RTX 3050 range)
            return 8, 4   # batch_size, workers
    else:
        return 4, 2  # Conservative for <4GB

def train_high_performance_yolo():
    """Train YOLOv8 with maximum GPU utilization"""
    
    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("❌ ultralytics not installed. Run: pip install ultralytics")
        return None
    
    # Optimize GPU settings
    gpu_memory = optimize_gpu_settings()
    if gpu_memory == 0:
        logger.error("❌ No GPU available for training")
        return None
    
    # Get optimal settings
    batch_size, workers = get_optimal_batch_size(gpu_memory)
    
    # High-performance configuration
    config = {
        'model_size': 'yolov8m.pt',  # Medium model for best balance
        'data_config': '../datasets/publaynet_yolo/publaynet.yaml',
        'epochs': 200,  # More epochs for better accuracy
        'batch_size': batch_size,
        'image_size': 640,
        'device': 'cuda',
        'workers': workers,
        'project': 'publaynet_training',
        'name': f'yolov8_high_performance_{int(time.time())}',
        
        # Performance optimizations
        'cache': 'ram',  # Cache images in RAM for speed
        'amp': True,     # Automatic Mixed Precision
        'optimizer': 'AdamW',  # Better optimizer
        'lr0': 0.01,     # Initial learning rate
        'lrf': 0.01,     # Final learning rate
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'box': 7.5,      # Box loss gain
        'cls': 0.5,      # Class loss gain
        'dfl': 1.5,      # DFL loss gain
        'pose': 12.0,    # Pose loss gain
        'kobj': 1.0,     # Keypoint obj loss gain
        'label_smoothing': 0.0,
        'nbs': 64,       # Nominal batch size
        'hsv_h': 0.015,  # Image HSV-Hue augmentation
        'hsv_s': 0.7,    # Image HSV-Saturation augmentation
        'hsv_v': 0.4,    # Image HSV-Value augmentation
        'degrees': 0.0,  # Image rotation (+/- deg)
        'translate': 0.1, # Image translation (+/- fraction)
        'scale': 0.5,    # Image scale (+/- gain)
        'shear': 0.0,    # Image shear (+/- deg)
        'perspective': 0.0, # Image perspective (+/- fraction)
        'flipud': 0.0,   # Image flip up-down (probability)
        'fliplr': 0.5,   # Image flip left-right (probability)
        'mosaic': 1.0,   # Image mosaic (probability)
        'mixup': 0.0,    # Image mixup (probability)
        'copy_paste': 0.0 # Segment copy-paste (probability)
    }
    
    # Check dataset
    if not os.path.exists(config['data_config']):
        logger.error(f"❌ Dataset config not found: {config['data_config']}")
        logger.info("Please run: python convert_publaynet_to_yolo.py first")
        return None
    
    # Display high-performance configuration
    logger.info("🔥 HIGH-PERFORMANCE TRAINING CONFIGURATION:")
    logger.info("=" * 60)
    logger.info(f"   🎯 Model: {config['model_size']}")
    logger.info(f"   📊 Epochs: {config['epochs']}")
    logger.info(f"   🚀 Batch Size: {config['batch_size']} (Optimized for {gpu_memory:.1f}GB GPU)")
    logger.info(f"   👥 Workers: {config['workers']}")
    logger.info(f"   📐 Image Size: {config['image_size']}")
    logger.info(f"   💾 Cache: {config['cache']}")
    logger.info(f"   ⚡ AMP: {config['amp']}")
    logger.info(f"   🧠 Optimizer: {config['optimizer']}")
    logger.info("=" * 60)
    
    try:
        # Load model
        logger.info("📥 Loading YOLOv8 model...")
        model = YOLO(config['model_size'])
        
        # Check for resume
        checkpoint_path = f"{config['project']}/{config['name']}/weights/last.pt"
        resume_training = os.path.exists(checkpoint_path)
        
        if resume_training:
            logger.info(f"🔄 Resuming from: {checkpoint_path}")
            model = YOLO(checkpoint_path)
        
        logger.info("🚀 STARTING HIGH-PERFORMANCE TRAINING...")
        logger.info("⏱️ This will take several hours for maximum accuracy")
        logger.info("🛑 Press Ctrl+C to stop and save checkpoint")
        
        # Start training with all optimizations
        results = model.train(
            data=config['data_config'],
            epochs=config['epochs'],
            imgsz=config['image_size'],
            batch=config['batch_size'],
            device=config['device'],
            workers=config['workers'],
            project=config['project'],
            name=config['name'],
            
            # Performance settings
            cache=config['cache'],
            amp=config['amp'],
            optimizer=config['optimizer'],
            lr0=config['lr0'],
            lrf=config['lrf'],
            momentum=config['momentum'],
            weight_decay=config['weight_decay'],
            warmup_epochs=config['warmup_epochs'],
            warmup_momentum=config['warmup_momentum'],
            warmup_bias_lr=config['warmup_bias_lr'],
            
            # Loss settings
            box=config['box'],
            cls=config['cls'],
            dfl=config['dfl'],
            
            # Augmentation settings
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
            
            # Training settings
            save=True,
            save_period=10,  # Save every 10 epochs
            val=True,
            plots=True,
            verbose=True,
            resume=resume_training,
            patience=50,
            exist_ok=True,
            
            # Additional performance settings
            single_cls=False,
            rect=False,  # Rectangular training
            cos_lr=True,  # Cosine learning rate scheduler
            close_mosaic=10  # Disable mosaic in final epochs
        )
        
        # Save final model
        model_save_path = f"models/yolov8_high_performance.pt"
        os.makedirs("models", exist_ok=True)
        model.save(model_save_path)
        
        logger.info("🎉 HIGH-PERFORMANCE TRAINING COMPLETED!")
        logger.info(f"📁 Model saved: {model_save_path}")
        logger.info(f"📊 Results: {config['project']}/{config['name']}")
        
        return model_save_path
        
    except torch.cuda.OutOfMemoryError:
        logger.error("❌ GPU OUT OF MEMORY!")
        logger.error(f"Current batch size: {config['batch_size']}")
        logger.error("Try reducing batch size or image size")
        return None
        
    except KeyboardInterrupt:
        logger.info("🛑 Training stopped by user - checkpoint saved")
        return None
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return None

if __name__ == "__main__":
    logger.info("🔥 HIGH-PERFORMANCE YOLO TRAINING")
    logger.info("🚀 Optimized for maximum GPU utilization")
    logger.info("=" * 60)
    
    model_path = train_high_performance_yolo()
    
    if model_path:
        logger.info("✅ SUCCESS! Your high-performance model is ready!")
        logger.info(f"🎯 Model location: {model_path}")
    else:
        logger.error("❌ Training failed")
