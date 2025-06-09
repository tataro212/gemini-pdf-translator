#!/usr/bin/env python3
"""
Test script to verify PyTorch CUDA installation and functionality
"""

import torch
import sys

def test_pytorch_cuda():
    """Test PyTorch CUDA installation and functionality"""
    print("=" * 60)
    print("PyTorch CUDA Installation Test")
    print("=" * 60)
    
    # Basic PyTorch info
    print(f"PyTorch version: {torch.__version__}")
    print(f"Python version: {sys.version}")
    
    # CUDA availability
    print(f"\nCUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"cuDNN version: {torch.backends.cudnn.version()}")
        print(f"Number of CUDA devices: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"Device {i}: {torch.cuda.get_device_name(i)}")
            print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.1f} GB")
        
        # Test tensor operations on GPU
        print("\nTesting tensor operations on GPU...")
        try:
            # Create tensors on GPU
            x = torch.randn(1000, 1000).cuda()
            y = torch.randn(1000, 1000).cuda()
            
            # Perform matrix multiplication
            z = torch.mm(x, y)
            
            print("✓ GPU tensor operations successful!")
            print(f"Result tensor shape: {z.shape}")
            print(f"Result tensor device: {z.device}")
            
        except Exception as e:
            print(f"✗ GPU tensor operations failed: {e}")
    else:
        print("CUDA is not available. Possible issues:")
        print("- PyTorch was installed without CUDA support")
        print("- NVIDIA drivers are not properly installed")
        print("- CUDA toolkit is not compatible")
    
    print("=" * 60)

if __name__ == "__main__":
    test_pytorch_cuda()
