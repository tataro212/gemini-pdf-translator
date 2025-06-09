"""
Test Script for Intelligent PDF Translation Pipeline

This script demonstrates the new intelligent, dynamic processing pipeline
and compares it with the standard workflow.
"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the main workflow
try:
    from main_workflow import UltimatePDFTranslator
    from config_manager import config_manager
    from utils import choose_input_path, choose_base_output_directory
    MAIN_WORKFLOW_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import main workflow: {e}")
    MAIN_WORKFLOW_AVAILABLE = False
    sys.exit(1)


class IntelligentPipelineDemo:
    """Demonstration of the intelligent pipeline capabilities."""
    
    def __init__(self):
        """Initialize the demo."""
        self.translator = UltimatePDFTranslator()
        self.results = {}
    
    async def run_demo(self, pdf_path: str, output_dir: str):
        """
        Run a comprehensive demo of the intelligent pipeline.
        
        Args:
            pdf_path: Path to the PDF file to process
            output_dir: Base output directory for results
        """
        logger.info("🚀 Starting Intelligent Pipeline Demo")
        logger.info(f"📄 Input PDF: {pdf_path}")
        logger.info(f"📁 Output Directory: {output_dir}")
        
        # Test 1: Intelligent Pipeline (if available)
        if hasattr(self.translator, 'intelligent_pipeline') and self.translator.intelligent_pipeline:
            await self._test_intelligent_pipeline(pdf_path, output_dir)
        else:
            logger.warning("⚠️ Intelligent pipeline not available")
        
        # Test 2: Advanced Pipeline (for comparison)
        if hasattr(self.translator, 'advanced_pipeline') and self.translator.advanced_pipeline:
            await self._test_advanced_pipeline(pdf_path, output_dir)
        else:
            logger.warning("⚠️ Advanced pipeline not available")
        
        # Test 3: Standard Pipeline (baseline)
        await self._test_standard_pipeline(pdf_path, output_dir)
        
        # Generate comparison report
        self._generate_comparison_report()
    
    async def _test_intelligent_pipeline(self, pdf_path: str, output_dir: str):
        """Test the intelligent pipeline."""
        logger.info("🧠 Testing Intelligent Pipeline")
        
        intelligent_output_dir = os.path.join(output_dir, "intelligent_pipeline")
        os.makedirs(intelligent_output_dir, exist_ok=True)
        
        start_time = time.time()
        
        try:
            # Force intelligent pipeline usage
            original_setting = self.translator.use_intelligent_pipeline
            self.translator.use_intelligent_pipeline = True
            
            result = await self.translator.translate_document_async(
                pdf_path, intelligent_output_dir
            )
            
            processing_time = time.time() - start_time
            
            self.results['intelligent'] = {
                'success': True,
                'processing_time': processing_time,
                'output_dir': intelligent_output_dir,
                'result': result
            }
            
            logger.info(f"✅ Intelligent pipeline completed in {processing_time:.2f}s")
            
            # Get performance summary if available
            if hasattr(self.translator.intelligent_pipeline, 'get_performance_summary'):
                performance_summary = self.translator.intelligent_pipeline.get_performance_summary()
                self.results['intelligent']['performance_summary'] = performance_summary
                logger.info(f"📊 Performance Summary: {performance_summary}")
            
            # Restore original setting
            self.translator.use_intelligent_pipeline = original_setting
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Intelligent pipeline failed: {e}")
            
            self.results['intelligent'] = {
                'success': False,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    async def _test_advanced_pipeline(self, pdf_path: str, output_dir: str):
        """Test the advanced pipeline."""
        logger.info("🎯 Testing Advanced Pipeline")
        
        advanced_output_dir = os.path.join(output_dir, "advanced_pipeline")
        os.makedirs(advanced_output_dir, exist_ok=True)
        
        start_time = time.time()
        
        try:
            # Force advanced pipeline usage
            original_intelligent = self.translator.use_intelligent_pipeline
            original_advanced = self.translator.use_advanced_features
            
            self.translator.use_intelligent_pipeline = False
            self.translator.use_advanced_features = True
            
            result = await self.translator.translate_document_async(
                pdf_path, advanced_output_dir
            )
            
            processing_time = time.time() - start_time
            
            self.results['advanced'] = {
                'success': True,
                'processing_time': processing_time,
                'output_dir': advanced_output_dir,
                'result': result
            }
            
            logger.info(f"✅ Advanced pipeline completed in {processing_time:.2f}s")
            
            # Restore original settings
            self.translator.use_intelligent_pipeline = original_intelligent
            self.translator.use_advanced_features = original_advanced
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Advanced pipeline failed: {e}")
            
            self.results['advanced'] = {
                'success': False,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    async def _test_standard_pipeline(self, pdf_path: str, output_dir: str):
        """Test the standard pipeline."""
        logger.info("📝 Testing Standard Pipeline")
        
        standard_output_dir = os.path.join(output_dir, "standard_pipeline")
        os.makedirs(standard_output_dir, exist_ok=True)
        
        start_time = time.time()
        
        try:
            # Force standard pipeline usage
            original_intelligent = self.translator.use_intelligent_pipeline
            original_advanced = self.translator.use_advanced_features
            
            self.translator.use_intelligent_pipeline = False
            self.translator.use_advanced_features = False
            
            result = await self.translator.translate_document_async(
                pdf_path, standard_output_dir
            )
            
            processing_time = time.time() - start_time
            
            self.results['standard'] = {
                'success': True,
                'processing_time': processing_time,
                'output_dir': standard_output_dir,
                'result': result
            }
            
            logger.info(f"✅ Standard pipeline completed in {processing_time:.2f}s")
            
            # Restore original settings
            self.translator.use_intelligent_pipeline = original_intelligent
            self.translator.use_advanced_features = original_advanced
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Standard pipeline failed: {e}")
            
            self.results['standard'] = {
                'success': False,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    def _generate_comparison_report(self):
        """Generate a comprehensive comparison report."""
        logger.info("📊 Generating Comparison Report")
        
        report = """
🎉 INTELLIGENT PIPELINE DEMO RESULTS
=====================================

"""
        
        for pipeline_name, result in self.results.items():
            pipeline_title = pipeline_name.replace('_', ' ').title()
            
            if result['success']:
                report += f"""
{pipeline_title} Pipeline:
✅ Status: SUCCESS
⏱️ Processing Time: {result['processing_time']:.2f} seconds
📁 Output Directory: {result.get('output_dir', 'N/A')}
"""
                
                # Add performance summary for intelligent pipeline
                if pipeline_name == 'intelligent' and 'performance_summary' in result:
                    perf = result['performance_summary']
                    report += f"""
📊 Performance Metrics:
   • Total Documents: {perf.get('total_documents_processed', 0)}
   • Average Quality: {perf.get('average_quality_score', 0):.2f}
   • Cache Hit Rate: {perf.get('cache_hit_rate', 0):.2%}
   • Cost Savings: {perf.get('total_cost_savings', 0):.1f}%
"""
            else:
                report += f"""
{pipeline_title} Pipeline:
❌ Status: FAILED
⏱️ Processing Time: {result['processing_time']:.2f} seconds
🚫 Error: {result.get('error', 'Unknown error')}
"""
        
        # Performance comparison
        if len([r for r in self.results.values() if r['success']]) > 1:
            report += "\n🏆 PERFORMANCE COMPARISON:\n"
            
            successful_results = {k: v for k, v in self.results.items() if v['success']}
            fastest = min(successful_results.items(), key=lambda x: x[1]['processing_time'])
            
            report += f"🥇 Fastest: {fastest[0].title()} ({fastest[1]['processing_time']:.2f}s)\n"
            
            for name, result in successful_results.items():
                if name != fastest[0]:
                    time_diff = result['processing_time'] - fastest[1]['processing_time']
                    report += f"   {name.title()}: +{time_diff:.2f}s slower\n"
        
        report += """

💡 RECOMMENDATIONS:
• Use Intelligent Pipeline for complex documents with mixed content
• Use Advanced Pipeline for documents requiring high-quality translation
• Use Standard Pipeline for simple documents or when resources are limited

🔧 CONFIGURATION:
• Enable intelligent pipeline: set use_intelligent_pipeline = True in config.ini
• Adjust strategy: set tool_selection_strategy = balanced|cost_optimized|quality_focused
• Enable semantic cache: set enable_semantic_cache = True
"""
        
        logger.info(report)


async def main():
    """Main demo function."""
    if not MAIN_WORKFLOW_AVAILABLE:
        logger.error("Main workflow not available. Please check dependencies.")
        return
    
    # Get input file and output directory
    try:
        pdf_path = choose_input_path()
        if not pdf_path:
            logger.error("No input file selected")
            return
        
        output_base_dir = choose_base_output_directory()
        if not output_base_dir:
            logger.error("No output directory selected")
            return
        
        # Create demo-specific output directory
        demo_output_dir = os.path.join(output_base_dir, "intelligent_pipeline_demo")
        os.makedirs(demo_output_dir, exist_ok=True)
        
        # Run the demo
        demo = IntelligentPipelineDemo()
        await demo.run_demo(pdf_path, demo_output_dir)
        
        logger.info("🎉 Demo completed successfully!")
        logger.info(f"📁 Results saved to: {demo_output_dir}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
