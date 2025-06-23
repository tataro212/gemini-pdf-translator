#!/usr/bin/env python3
"""
Simple YOLO Training Script for Document Layout Analysis
Supports training different YOLO model sizes and configurations
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_model(model_size='n', dataset='publaynet', epochs=100, batch_size=8, device='0'):
    """
    Train a YOLO model with specified parameters
    
    Args:
        model_size: 'n' (nano), 's' (small), 'm' (medium), 'l' (large), 'x' (xlarge)
        dataset: 'publaynet', 'doclaynet', or 'merged'
        epochs: number of training epochs
        batch_size: batch size for training (default 8 for RTX 3050 4GB)
        device: device to use ('0' for GPU, 'cpu' for CPU)
    """
    
    # Model mapping
    model_map = {
        'n': 'yolov8n.pt',
        's': 'yolov8s.pt', 
        'm': 'yolov8m.pt',
        'l': 'yolov8l.pt',
        'x': 'yolov8x.pt'
    }
    
    # Dataset mapping
    dataset_map = {
        'publaynet': 'C:/Users/30694/datasets/publaynet_yolo/publaynet.yaml',
        'doclaynet': 'C:/Users/30694/datasets/my_dataset.yaml',
        'merged': 'merged_dataset_config.yaml'
    }
    
    if model_size not in model_map:
        raise ValueError(f"Invalid model size: {model_size}. Choose from {list(model_map.keys())}")
    
    if dataset not in dataset_map:
        raise ValueError(f"Invalid dataset: {dataset}. Choose from {list(dataset_map.keys())}")
    
    # Get model and dataset paths
    model_path = model_map[model_size]
    dataset_path = dataset_map[dataset]
    
    # Create output directory
    output_dir = f"runs/train_yolo{model_size}_{dataset}"
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"🚀 Starting YOLO training:")
    logger.info(f"   Model: {model_path}")
    logger.info(f"   Dataset: {dataset_path}")
    logger.info(f"   Epochs: {epochs}")
    logger.info(f"   Batch size: {batch_size}")
    logger.info(f"   Device: {device}")
    logger.info(f"   Output: {output_dir}")
    
    try:
        # Initialize model
        model = YOLO(model_path)
        
        # Start training
        results = model.train(
            data=dataset_path,
            epochs=epochs,
            imgsz=640,
            batch=batch_size,
            device=device,
            project=output_dir,
            name=f"yolo{model_size}_{dataset}",
            patience=20,
            save_period=10,
            cache=False,
            workers=4
        )
        
        logger.info(f"✅ Training completed! Results saved in {output_dir}")
        
        # Get best model path
        best_model = Path(results.save_dir) / "weights" / "best.pt"
        if best_model.exists():
            logger.info(f"Best model saved at: {best_model}")
            return str(best_model)
        else:
            logger.warning("Best model not found")
            return None
            
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        raise

def compare_models():
    """Compare different YOLO model sizes"""
    logger.info("🔍 Comparing YOLO model sizes...")
    
    models = ['n', 's', 'm', 'l', 'x']
    results = {}
    
    for model_size in models:
        try:
            logger.info(f"Training YOLO{model_size}...")
            best_model = train_model(
                model_size=model_size,
                dataset='publaynet',  # Use PubLayNet for comparison
                epochs=50,  # Shorter training for comparison
                batch_size=8  # Smaller batch size for larger models
            )
            results[model_size] = best_model
        except Exception as e:
            logger.error(f"Failed to train YOLO{model_size}: {e}")
            results[model_size] = None
    
    # Print comparison results
    print("\n" + "="*60)
    print("MODEL COMPARISON RESULTS")
    print("="*60)
    for model_size, model_path in results.items():
        status = "✅ Success" if model_path else "❌ Failed"
        print(f"YOLO{model_size}: {status}")
        if model_path:
            print(f"  Model: {model_path}")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Train YOLO models for document layout analysis')
    parser.add_argument('--model', type=str, default='n', choices=['n', 's', 'm', 'l', 'x'],
                       help='YOLO model size (n=nano, s=small, m=medium, l=large, x=xlarge)')
    parser.add_argument('--dataset', type=str, default='publaynet', 
                       choices=['publaynet', 'doclaynet', 'merged'],
                       help='Dataset to use for training')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size for training')
    parser.add_argument('--device', type=str, default='0', help='Device to use (0 for GPU, cpu for CPU)')
    parser.add_argument('--compare', action='store_true', help='Compare all model sizes')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_models()
    else:
        train_model(
            model_size=args.model,
            dataset=args.dataset,
            epochs=args.epochs,
            batch_size=args.batch_size,
            device=args.device
        )

if __name__ == "__main__":
    main() 