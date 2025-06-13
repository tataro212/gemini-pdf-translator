#!/usr/bin/env python3
"""
Simple system check for YOLO training
"""

import sys

def check_system():
    print("🔍 SYSTEM CHECK FOR YOLO TRAINING")
    print("=" * 40)
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    
    # Check PyTorch and CUDA
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("❌ No GPU detected")
            
    except ImportError:
        print("❌ PyTorch not installed")
    
    # Check Ultralytics
    try:
        import ultralytics
        print(f"✅ Ultralytics: {ultralytics.__version__}")
    except ImportError:
        print("❌ Ultralytics not installed - run: pip install ultralytics")
    
    # Check dataset
    import os
    dataset_path = "../datasets/publaynet_yolo/publaynet.yaml"
    if os.path.exists(dataset_path):
        print("✅ Dataset ready")
    else:
        print("❌ Dataset missing - run convert_publaynet_to_yolo.py first")
    
    print("=" * 40)
    print("✅ System check complete!")

if __name__ == "__main__":
    check_system()
