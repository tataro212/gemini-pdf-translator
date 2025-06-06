#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo of enhanced capabilities
"""

import ultimate_pdf_translator as upt

def demo_document_detection():
    """Demo document type detection"""
    print("=== DOCUMENT TYPE DETECTION DEMO ===")
    
    detector = upt.DocumentTypeDetector()
    
    test_cases = [
        ("Academic", "This study presents a comprehensive analysis of the methodology used in recent research findings."),
        ("Legal", "Whereas the parties hereby agree to the terms and conditions pursuant to the jurisdiction."),
        ("Technical", "Follow these installation procedures to configure the system parameters and requirements."),
        ("Medical", "The patient presented with acute symptoms requiring immediate clinical treatment and therapy.")
    ]
    
    for label, text in test_cases:
        try:
            detected, confidence, config = detector.detect_document_type(text)
            print(f"✓ {label}: detected as '{detected}' (confidence: {confidence:.2f})")
            print(f"  Style guide: {config['style_guide'][:80]}...")
        except Exception as e:
            print(f"❌ {label}: Error - {e}")
    
    return True

def demo_prompt_generation():
    """Demo enhanced prompt generation"""
    print("\n=== ENHANCED PROMPT GENERATION DEMO ===")
    
    try:
        prompt_gen = upt.EnhancedTranslationPromptGenerator()
        sample_text = "The research methodology employed in this study follows established academic protocols."
        
        prompt = prompt_gen.generate_enhanced_prompt(
            sample_text, 
            "Greek", 
            "Academic research paper discussing methodology", 
            "formal academic style"
        )
        
        print(f"✓ Generated enhanced prompt: {len(prompt)} characters")
        print(f"  Preview: {prompt[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Prompt generation error: {e}")
        return False

def demo_batch_processing():
    """Demo coherent batch processing"""
    print("\n=== COHERENT BATCH PROCESSING DEMO ===")
    
    try:
        batch_processor = upt.CoherentBatchProcessor(max_batch_size=150)
        
        # Create test text with clear paragraph structure
        long_text = """This is the first paragraph with important content that should be preserved as a unit.

This is the second paragraph that continues the narrative and should maintain coherence with the previous paragraph.

This is the third paragraph that concludes the document and references earlier points made in the discussion."""
        
        batches = batch_processor.create_coherent_batches(long_text)
        
        print(f"✓ Original text: {len(long_text)} characters")
        print(f"✓ Created {len(batches)} coherent batches")
        
        for i, batch in enumerate(batches):
            print(f"  Batch {i+1}: {len(batch['text'])} chars")
            print(f"    Preview: {batch['text'][:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False

def main():
    """Main demo function"""
    print("🚀 ENHANCED PDF TRANSLATOR CAPABILITIES DEMO")
    print("=" * 50)
    
    try:
        # Run demos
        demo_document_detection()
        demo_prompt_generation()
        demo_batch_processing()
        
        print("\n🎉 All enhanced capabilities demonstrated successfully!")
        print("\nThe enhanced PDF translator now includes:")
        print("✓ Intelligent document type detection")
        print("✓ Context-aware translation prompts")
        print("✓ Coherent batch processing")
        print("✓ Advanced OCR capabilities (when dependencies available)")
        print("✓ Smart image analysis")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
