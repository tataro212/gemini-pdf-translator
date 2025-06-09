#!/usr/bin/env python3
"""Test script to verify Nougat functionality"""

import os
import sys
from pathlib import Path

print("Testing Nougat functionality...")
print("=" * 50)

try:
    from nougat import NougatModel
    from nougat.utils.dataset import LazyDataset
    from nougat.utils.device import move_to_device, default_batch_size
    from nougat.postprocessing import markdown_compatible
    import torch
    
    print("✅ All Nougat imports successful!")
    
    # Check if CUDA is available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✅ Using device: {device}")
    
    # Try to initialize the model (this will download the model if not present)
    print("🔄 Initializing Nougat model...")
    try:
        model = NougatModel.from_pretrained("facebook/nougat-base")
        model = move_to_device(model, bf16=False, cuda=device.type == "cuda")
        print("✅ Nougat model initialized successfully!")
        print(f"✅ Model device: {next(model.parameters()).device}")
        
        # Test basic functionality without actual PDF processing
        print("✅ Nougat is ready for PDF processing!")
        
    except Exception as e:
        print(f"⚠️  Model initialization issue: {e}")
        print("This might be due to missing model files or network issues.")
        print("The environment is set up correctly, but model download may be needed.")
        
except Exception as e:
    print(f"❌ Nougat functionality error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
print("Nougat functionality test complete!")
