#!/usr/bin/env python3
"""
Test script for memory-aware Nougat parallel processing.
This script tests the memory constraints and worker limits.
"""

import os
import logging
from nougat_integration import NougatIntegration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_system_memory():
    """Check system memory availability"""
    print("\n💾 CHECKING SYSTEM MEMORY")
    print("=" * 60)
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        used_gb = memory.used / (1024**3)
        percent_used = memory.percent
        
        print(f"📊 Total RAM: {total_gb:.1f} GB")
        print(f"📊 Used RAM: {used_gb:.1f} GB ({percent_used:.1f}%)")
        print(f"📊 Available RAM: {available_gb:.1f} GB")
        
        # Calculate how many Nougat instances we can safely run
        memory_per_nougat = 3.0  # GB
        max_instances = int(available_gb // memory_per_nougat)
        
        print(f"\n🧮 Memory calculation:")
        print(f"   Memory per Nougat instance: {memory_per_nougat} GB")
        print(f"   Max safe parallel instances: {max_instances}")
        
        if max_instances < 2:
            print("⚠️  WARNING: Insufficient memory for parallel processing")
            print("   Recommendation: Use sequential processing only")
        elif max_instances == 2:
            print("✅ Memory sufficient for 2 parallel workers (recommended)")
        else:
            print(f"✅ Memory sufficient for {max_instances} workers (will be limited to 2 for stability)")
        
        return available_gb, max_instances
        
    except ImportError:
        print("❌ psutil not installed - cannot check memory")
        print("   Install with: pip install psutil")
        return None, None
    except Exception as e:
        print(f"❌ Error checking memory: {e}")
        return None, None

def test_memory_aware_decision():
    """Test the memory-aware parallel processing decision"""
    print("\n🧪 TESTING MEMORY-AWARE PARALLEL PROCESSING")
    print("=" * 60)
    
    nougat = NougatIntegration()
    
    # Test memory checking
    available_memory = nougat._check_available_memory()
    print(f"📊 Available memory detected: {available_memory:.1f} GB")
    
    # Test different batch scenarios
    test_scenarios = [
        {"total_batches": 1, "description": "Single batch"},
        {"total_batches": 2, "description": "Two batches"},
        {"total_batches": 4, "description": "Four batches"},
        {"total_batches": 8, "description": "Eight batches"},
    ]
    
    print(f"\n📋 Testing parallel processing decisions:")
    for scenario in test_scenarios:
        total_batches = scenario["total_batches"]
        description = scenario["description"]
        
        use_parallel = nougat._should_use_parallel_batching(total_batches)
        processing_type = "🚀 PARALLEL" if use_parallel else "📄 SEQUENTIAL"
        
        print(f"   {description}: {processing_type}")

def test_worker_count_calculation():
    """Test worker count calculation with memory constraints"""
    print("\n🔢 TESTING WORKER COUNT CALCULATION")
    print("=" * 60)
    
    nougat = NougatIntegration()
    available_memory = nougat._check_available_memory()
    
    # Simulate the calculation logic
    memory_needed_per_worker = 3.0  # GB
    max_workers_by_memory = int(available_memory // memory_needed_per_worker)
    
    import multiprocessing
    available_cores = max(1, multiprocessing.cpu_count() - 1)
    max_workers_by_cores = available_cores // 4
    
    print(f"📊 Resource constraints:")
    print(f"   Available memory: {available_memory:.1f} GB")
    print(f"   Memory per worker: {memory_needed_per_worker} GB")
    print(f"   Max workers by memory: {max_workers_by_memory}")
    print(f"   Available CPU cores: {available_cores}")
    print(f"   Max workers by cores: {max_workers_by_cores}")
    
    final_max_workers = min(max_workers_by_cores, max_workers_by_memory, 2)
    print(f"   Final max workers: {final_max_workers}")
    
    if final_max_workers < 2:
        print("⚠️  Result: Sequential processing only")
    else:
        print(f"✅ Result: Parallel processing with {final_max_workers} workers")

def main():
    """Run all tests"""
    print("🚀 MEMORY-AWARE NOUGAT PROCESSING - TEST SUITE")
    print("=" * 60)
    print("Testing memory constraints for parallel Nougat processing")
    print()
    
    # Test 1: Check system memory
    available_gb, max_instances = check_system_memory()
    
    # Test 2: Test memory-aware decision logic
    test_memory_aware_decision()
    
    # Test 3: Test worker count calculation
    test_worker_count_calculation()
    
    # Summary and recommendations
    print("\n📊 SUMMARY AND RECOMMENDATIONS")
    print("=" * 60)
    
    if available_gb is not None:
        if available_gb < 6:
            print("⚠️  LOW MEMORY SYSTEM:")
            print(f"   Available: {available_gb:.1f} GB")
            print("   Recommendation: Use sequential processing only")
            print("   Parallel processing will likely cause OOM errors")
        elif available_gb < 10:
            print("✅ MODERATE MEMORY SYSTEM:")
            print(f"   Available: {available_gb:.1f} GB")
            print("   Recommendation: Use 2 parallel workers maximum")
            print("   Monitor memory usage during processing")
        else:
            print("✅ HIGH MEMORY SYSTEM:")
            print(f"   Available: {available_gb:.1f} GB")
            print("   Recommendation: 2 parallel workers (limited for stability)")
            print("   Could potentially handle more workers")
    
    print("\n🔧 MEMORY OPTIMIZATION TIPS:")
    print("   1. Close other applications before processing large PDFs")
    print("   2. Use smaller batch sizes (25-30 pages) to reduce memory peaks")
    print("   3. Monitor system memory during processing")
    print("   4. Consider sequential processing for very large documents")
    print("   5. Each Nougat worker needs ~3GB RAM for model loading")

if __name__ == "__main__":
    main()
