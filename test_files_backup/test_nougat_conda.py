#!/usr/bin/env python3
"""Test script for Nougat in Conda environment"""

print("Testing Nougat in Conda environment...")
print("=" * 50)

try:
    import torch
    print(f"✅ PyTorch version: {torch.__version__}")
    print(f"✅ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"❌ PyTorch error: {e}")

try:
    import transformers
    print(f"✅ Transformers version: {transformers.__version__}")
except Exception as e:
    print(f"❌ Transformers error: {e}")

try:
    import tokenizers
    print(f"✅ Tokenizers version: {tokenizers.__version__}")
except Exception as e:
    print(f"❌ Tokenizers error: {e}")

try:
    import nougat
    print(f"✅ Nougat imported successfully!")
    print(f"✅ Nougat version: {getattr(nougat, '__version__', 'Unknown')}")
except Exception as e:
    print(f"❌ Nougat error: {e}")

print("=" * 50)
print("Environment test complete!")
