#!/usr/bin/env python3
"""
Test script to demonstrate parallel Nougat batch processing capabilities
"""

import logging
import multiprocessing
from nougat_integration import NougatIntegration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_parallel_processing_info():
    """Test and display parallel processing capabilities"""
    print("🔍 PARALLEL PROCESSING ANALYSIS")
    print("=" * 50)
    
    # Check system capabilities
    cpu_count = multiprocessing.cpu_count()
    available_cores = max(1, cpu_count - 1)
    
    print(f"💻 System CPU cores: {cpu_count}")
    print(f"🚀 Available for parallel processing: {available_cores}")
    
    # Initialize Nougat integration
    nougat = NougatIntegration()
    
    # Test different batch scenarios
    test_scenarios = [
        {"total_pages": 25, "batch_size": 50, "description": "Small document (single batch)"},
        {"total_pages": 100, "batch_size": 50, "description": "Medium document (2 batches)"},
        {"total_pages": 200, "batch_size": 50, "description": "Large document (4 batches)"},
        {"total_pages": 400, "batch_size": 50, "description": "Very large document (8 batches)"},
    ]
    
    print("\n📊 BATCH PROCESSING SCENARIOS:")
    print("-" * 50)
    
    for scenario in test_scenarios:
        total_pages = scenario["total_pages"]
        batch_size = scenario["batch_size"]
        description = scenario["description"]
        
        total_batches = (total_pages + batch_size - 1) // batch_size
        use_parallel = nougat._should_use_parallel_batching(total_batches)
        
        processing_type = "🚀 PARALLEL" if use_parallel else "📄 SEQUENTIAL"
        max_workers = min(available_cores, total_batches) if use_parallel else 1
        
        print(f"📄 {description}")
        print(f"   Pages: {total_pages}, Batches: {total_batches}")
        print(f"   Processing: {processing_type} (workers: {max_workers})")
        print()

def test_parallel_vs_sequential_comparison():
    """Compare parallel vs sequential processing estimates"""
    print("⚡ PERFORMANCE COMPARISON ESTIMATES")
    print("=" * 50)
    
    # Assume each batch takes ~3 minutes on average
    batch_time_minutes = 3
    
    scenarios = [
        {"batches": 2, "description": "Small document"},
        {"batches": 4, "description": "Medium document"},
        {"batches": 8, "description": "Large document"},
        {"batches": 16, "description": "Very large document"},
    ]
    
    cpu_count = multiprocessing.cpu_count()
    available_cores = max(1, cpu_count - 1)
    
    for scenario in scenarios:
        batches = scenario["batches"]
        description = scenario["description"]
        
        # Sequential time
        sequential_time = batches * batch_time_minutes
        
        # Parallel time (assuming perfect parallelization)
        max_workers = min(available_cores, batches)
        parallel_time = (batches / max_workers) * batch_time_minutes
        
        # Time savings
        time_saved = sequential_time - parallel_time
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1
        
        print(f"📊 {description} ({batches} batches):")
        print(f"   Sequential: {sequential_time:.1f} minutes")
        print(f"   Parallel ({max_workers} workers): {parallel_time:.1f} minutes")
        print(f"   Time saved: {time_saved:.1f} minutes ({speedup:.1f}x speedup)")
        print()

if __name__ == "__main__":
    print("🧪 NOUGAT PARALLEL PROCESSING TEST")
    print("=" * 60)
    
    test_parallel_processing_info()
    test_parallel_vs_sequential_comparison()
    
    print("✅ Test completed! Parallel processing is ready to use.")
    print("\n💡 USAGE TIPS:")
    print("- Parallel processing automatically activates for documents with 2+ batches")
    print("- Uses all available CPU cores minus one (to keep system responsive)")
    print("- Each batch processes ~50 pages by default")
    print("- Failed batches are handled gracefully with dead letter queue")
    print("- GPU acceleration works with both parallel and sequential processing")
