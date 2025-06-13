"""
EXTREME GPU Utilization YOLO Training
WARNING: This pushes your GPU to the absolute limit!
"""

import os
import torch
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extreme_gpu_training():
    """Train with EXTREME GPU utilization - use at your own risk!"""
    
    if not torch.cuda.is_available():
        logger.error("❌ No GPU available!")
        return
    
    # EXTREME GPU optimizations
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    torch.cuda.empty_cache()
    
    # Get GPU memory
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
    logger.info(f"🔥 EXTREME MODE: {gpu_memory:.1f}GB GPU")
    
    # AGGRESSIVE settings for RTX 3050 Laptop GPU
    if gpu_memory >= 4:
        batch_size = 16  # MAXIMUM batch size
        workers = 8      # MAXIMUM workers
        cache = 'ram'    # Cache everything in RAM
        image_size = 640 # Full resolution
    else:
        batch_size = 12
        workers = 6
        cache = 'ram'
        image_size = 640
    
    logger.warning("⚠️ EXTREME MODE ENABLED!")
    logger.warning("⚠️ This will use 95%+ of your GPU!")
    logger.warning("⚠️ Monitor temperatures!")
    
    config = {
        'model_size': 'yolov8l.pt',  # LARGE model for maximum accuracy
        'data_config': '../datasets/publaynet_yolo/publaynet.yaml',
        'epochs': 300,  # MAXIMUM epochs
        'batch_size': batch_size,
        'image_size': image_size,
        'device': 'cuda',
        'workers': workers,
        'project': 'publaynet_training',
        'name': f'yolov8_EXTREME_{int(torch.cuda.get_device_properties(0).total_memory/1e6)}MB',
        'cache': cache,
        'amp': True,
        'optimizer': 'AdamW',
        'lr0': 0.01,
        'lrf': 0.001,  # Lower final LR for fine-tuning
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'warmup_epochs': 5,
        'box': 7.5,
        'cls': 0.5,
        'dfl': 1.5,
        'nbs': 64,
        'cos_lr': True,
        'close_mosaic': 15
    }
    
    logger.info("🔥 EXTREME CONFIGURATION:")
    logger.info(f"   Model: {config['model_size']} (LARGE)")
    logger.info(f"   Batch: {config['batch_size']} (MAXIMUM)")
    logger.info(f"   Workers: {config['workers']} (MAXIMUM)")
    logger.info(f"   Epochs: {config['epochs']} (MAXIMUM)")
    logger.info(f"   Cache: {config['cache']} (RAM)")
    
    try:
        model = YOLO(config['model_size'])
        
        logger.info("🚀 STARTING EXTREME TRAINING...")
        logger.info("🌡️ MONITOR YOUR GPU TEMPERATURE!")
        
        results = model.train(
            data=config['data_config'],
            epochs=config['epochs'],
            imgsz=config['image_size'],
            batch=config['batch_size'],
            device=config['device'],
            workers=config['workers'],
            project=config['project'],
            name=config['name'],
            cache=config['cache'],
            amp=config['amp'],
            optimizer=config['optimizer'],
            lr0=config['lr0'],
            lrf=config['lrf'],
            momentum=config['momentum'],
            weight_decay=config['weight_decay'],
            warmup_epochs=config['warmup_epochs'],
            box=config['box'],
            cls=config['cls'],
            dfl=config['dfl'],
            nbs=config['nbs'],
            cos_lr=config['cos_lr'],
            close_mosaic=config['close_mosaic'],
            save=True,
            save_period=5,  # Save frequently
            val=True,
            plots=True,
            verbose=True,
            patience=100,  # More patience for extreme training
            exist_ok=True
        )
        
        model_path = f"models/yolov8_EXTREME.pt"
        os.makedirs("models", exist_ok=True)
        model.save(model_path)
        
        logger.info("🎉 EXTREME TRAINING COMPLETED!")
        logger.info(f"🏆 SUPREME MODEL: {model_path}")
        
        return model_path
        
    except torch.cuda.OutOfMemoryError:
        logger.error("💥 GPU MEMORY EXCEEDED!")
        logger.error("Reduce batch_size in the script and try again")
        return None
    except Exception as e:
        logger.error(f"❌ Extreme training failed: {e}")
        return None

if __name__ == "__main__":
    logger.warning("⚠️ EXTREME GPU TRAINING MODE ⚠️")
    response = input("This will push your GPU to 95%+ usage. Continue? (yes/no): ")
    if response.lower() == 'yes':
        extreme_gpu_training()
    else:
        logger.info("Training cancelled")
