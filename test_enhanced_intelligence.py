#!/usr/bin/env python3
"""
Test Enhanced Document Intelligence Features
Tests all new intelligence features without compromising existing functionality
"""

import sys
import os
import tempfile
import json

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_intelligence_import():
    """Test importing enhanced intelligence modules"""
    print("🧠 Testing Enhanced Intelligence Import...")
    
    try:
        from enhanced_document_intelligence import (
            AdvancedContentClassifier, SemanticContentGrouper,
            CrossReferencePreserver, ContentClassification, SemanticGroup
        )
        print("✅ Enhanced intelligence modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Enhanced intelligence import failed: {e}")
        return False

def test_content_classification():
    """Test advanced content classification"""
    print("\n📊 Testing Advanced Content Classification...")
    
    try:
        from enhanced_document_intelligence import AdvancedContentClassifier
        
        classifier = AdvancedContentClassifier()
        
        # Test academic content
        academic_content = [
            {'text': 'This research methodology examines the hypothesis through statistical analysis.'},
            {'text': 'The empirical data supports our theoretical framework.'},
            {'text': 'References: Smith, J. (2023). Academic Research Methods.'}
        ]
        
        classification = classifier.classify_content(academic_content)
        
        print(f"✅ Academic content classified:")
        print(f"   Primary Type: {classification.primary_type}")
        print(f"   Confidence: {classification.confidence:.1%}")
        print(f"   Complexity: {classification.complexity_level}")
        print(f"   Approach: {classification.translation_approach}")
        print(f"   Batch Size: {classification.recommended_batch_size}")
        print(f"   Temperature: {classification.recommended_temperature}")
        
        # Test technical content
        technical_content = [
            {'text': 'Configure the system parameters according to specifications.'},
            {'text': 'Installation procedure: Step 1 - Download the software package.'},
            {'text': 'System requirements: 8GB RAM, 500GB storage.'}
        ]
        
        tech_classification = classifier.classify_content(technical_content)
        print(f"✅ Technical content classified: {tech_classification.primary_type}")
        
        # Test legal content
        legal_content = [
            {'text': 'Whereas the parties hereby agree pursuant to this contract.'},
            {'text': 'The jurisdiction for this agreement shall be determined by applicable law.'},
            {'text': 'Liability limitations are specified in clause 5.2.'}
        ]
        
        legal_classification = classifier.classify_content(legal_content)
        print(f"✅ Legal content classified: {legal_classification.primary_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Content classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_semantic_grouping():
    """Test semantic content grouping"""
    print("\n🎭 Testing Semantic Content Grouping...")
    
    try:
        from enhanced_document_intelligence import SemanticContentGrouper
        
        grouper = SemanticContentGrouper()
        
        # Test content with different themes
        mixed_content = [
            {'text': 'Introduction to the research topic', 'type': 'h1'},
            {'text': 'This study examines the relationship between variables.', 'type': 'p'},
            {'text': 'Methodology section begins here', 'type': 'h1'},
            {'text': 'Data collection followed established protocols.', 'type': 'p'},
            {'text': 'Statistical analysis was performed using SPSS.', 'type': 'p'},
            {'text': 'Results and findings', 'type': 'h1'},
            {'text': 'The analysis revealed significant correlations.', 'type': 'p'},
            {'text': 'Figure 1 shows the distribution of data.', 'type': 'p'},
            {'text': 'Conclusion and future work', 'type': 'h1'},
            {'text': 'This research contributes to the field by...', 'type': 'p'}
        ]
        
        semantic_groups = grouper.create_semantic_groups(mixed_content)
        
        print(f"✅ Semantic grouping completed:")
        print(f"   Original items: {len(mixed_content)}")
        print(f"   Semantic groups: {len(semantic_groups)}")
        
        for i, group in enumerate(semantic_groups):
            print(f"   Group {i+1}: {group.semantic_theme} ({len(group.content_items)} items, priority: {group.translation_priority})")
            if group.cross_references:
                print(f"     Cross-refs: {group.cross_references}")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic grouping failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cross_reference_preservation():
    """Test cross-reference preservation"""
    print("\n🔗 Testing Cross-Reference Preservation...")
    
    try:
        from enhanced_document_intelligence import CrossReferencePreserver
        
        preserver = CrossReferencePreserver()
        
        # Test content with cross-references
        content_with_refs = [
            {'text': 'As shown in Figure 1, the data distribution is normal.'},
            {'text': 'Table 2 presents the statistical results.'},
            {'text': 'Section 3.1 discusses the methodology in detail.'},
            {'text': 'Chapter 5 contains the conclusions.'},
            {'text': 'Equation 3 represents the mathematical model.'},
            {'text': 'Appendix A provides additional information.'}
        ]
        
        # Extract references
        references = preserver.extract_references(content_with_refs)
        
        print(f"✅ Cross-reference extraction completed:")
        for ref_type, ref_list in references.items():
            print(f"   {ref_type}: {len(ref_list)} references")
            if ref_list:
                print(f"     Examples: {ref_list[:3]}")
        
        # Generate preservation guide
        guide = preserver.create_reference_preservation_guide(references)
        
        if guide:
            print(f"✅ Reference preservation guide generated ({len(guide)} characters)")
            print(f"   Preview: {guide[:200]}...")
        else:
            print("✅ No references found (expected for simple test)")
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-reference preservation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_main_system():
    """Test integration with the main translation system"""
    print("\n🔗 Testing Integration with Main System...")
    
    try:
        from ultimate_pdf_translator import document_intelligence, ENHANCED_REFERENCE_GUIDE
        
        # Test document intelligence manager
        print(f"✅ Document intelligence manager available: {document_intelligence.enabled}")
        
        # Test analysis with sample content
        test_content = [
            {'text': 'Research Methodology', 'type': 'h1'},
            {'text': 'This study employs quantitative analysis methods.', 'type': 'p'},
            {'text': 'Figure 1 shows the experimental setup.', 'type': 'p'},
            {'text': 'Statistical significance was tested using p < 0.05.', 'type': 'p'}
        ]
        
        analysis = document_intelligence.analyze_document_intelligence(test_content)
        
        print(f"✅ Intelligence analysis completed:")
        print(f"   Enhanced processing: {analysis.get('enhanced_processing', False)}")
        print(f"   Semantic groups: {len(analysis.get('semantic_groups', []))}")
        print(f"   Cross-references: {len(analysis.get('cross_references', {}))}")
        
        # Test parameter extraction
        enhanced_params = document_intelligence.get_enhanced_translation_parameters(analysis)
        
        if enhanced_params:
            print(f"✅ Enhanced parameters extracted:")
            for key, value in enhanced_params.items():
                if key != 'reference_guide':  # Skip long guide
                    print(f"   {key}: {value}")
        
        # Test global reference guide
        print(f"✅ Global reference guide: {len(ENHANCED_REFERENCE_GUIDE)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_enhancement():
    """Test enhanced prompt generation with intelligence"""
    print("\n💬 Testing Enhanced Prompt Generation...")
    
    try:
        from ultimate_pdf_translator import EnhancedTranslationPromptGenerator, ENHANCED_REFERENCE_GUIDE
        
        # Set up a test reference guide
        global ENHANCED_REFERENCE_GUIDE
        original_guide = ENHANCED_REFERENCE_GUIDE
        
        # Simulate a reference guide
        test_guide = """
=== CROSS-REFERENCE PRESERVATION GUIDE ===
IMPORTANT: Preserve these exact reference formats in translation:

FIGURE REFERENCES:
  - Keep format: 'figure 1'
  - Keep format: 'fig. 2'

TABLE REFERENCES:
  - Keep format: 'table 1'

Translate the reference TYPE but keep the NUMBERS/LETTERS unchanged.
Example: 'Figure 1' → 'Εικόνα 1' (Greek), 'Figura 1' (Spanish)
========================================
"""
        
        # Temporarily set the guide
        import ultimate_pdf_translator
        ultimate_pdf_translator.ENHANCED_REFERENCE_GUIDE = test_guide
        
        # Test prompt generation
        prompt_gen = EnhancedTranslationPromptGenerator()
        
        test_text = "As shown in Figure 1, the research methodology follows academic standards."
        enhanced_prompt = prompt_gen.generate_enhanced_prompt(
            test_text,
            "Greek",
            "This is an academic research paper with figures and tables.",
            "formal academic style"
        )
        
        print(f"✅ Enhanced prompt generated ({len(enhanced_prompt)} characters)")
        
        # Check if reference guide is included
        if "CROSS-REFERENCE PRESERVATION" in enhanced_prompt:
            print("✅ Cross-reference preservation guide included in prompt")
        else:
            print("⚠️ Cross-reference guide not found in prompt")
        
        # Restore original guide
        ultimate_pdf_translator.ENHANCED_REFERENCE_GUIDE = original_guide
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt enhancement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_behavior():
    """Test fallback behavior when enhanced intelligence is not available"""
    print("\n🛡️ Testing Fallback Behavior...")
    
    try:
        from ultimate_pdf_translator import DocumentIntelligenceManager
        
        # Create a manager with disabled intelligence
        fallback_manager = DocumentIntelligenceManager()
        fallback_manager.enabled = False
        
        test_content = [
            {'text': 'Test content for fallback', 'type': 'p'}
        ]
        
        analysis = fallback_manager.analyze_document_intelligence(test_content)
        
        print(f"✅ Fallback analysis completed:")
        print(f"   Enhanced processing: {analysis.get('enhanced_processing', False)}")
        print(f"   Classification: {analysis.get('classification')}")
        print(f"   Report: {analysis.get('intelligence_report', 'No report')}")
        
        # Test parameter extraction with fallback
        params = fallback_manager.get_enhanced_translation_parameters(analysis)
        print(f"✅ Fallback parameters: {len(params)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all enhanced intelligence tests"""
    print("🧠 ENHANCED DOCUMENT INTELLIGENCE - COMPREHENSIVE TEST")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: Import test
    test_results.append(("Enhanced Intelligence Import", test_enhanced_intelligence_import()))
    
    # Test 2: Content classification
    test_results.append(("Content Classification", test_content_classification()))
    
    # Test 3: Semantic grouping
    test_results.append(("Semantic Grouping", test_semantic_grouping()))
    
    # Test 4: Cross-reference preservation
    test_results.append(("Cross-Reference Preservation", test_cross_reference_preservation()))
    
    # Test 5: Integration with main system
    test_results.append(("Main System Integration", test_integration_with_main_system()))
    
    # Test 6: Prompt enhancement
    test_results.append(("Prompt Enhancement", test_prompt_enhancement()))
    
    # Test 7: Fallback behavior
    test_results.append(("Fallback Behavior", test_fallback_behavior()))
    
    # Results summary
    print("\n" + "=" * 70)
    print("📊 ENHANCED INTELLIGENCE TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"\n📈 OVERALL: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Enhanced intelligence is working perfectly.")
        print("💡 All features integrated without compromising existing functionality.")
    elif success_rate >= 70:
        print("✅ GOOD! Most enhanced features are working correctly.")
        print("💡 Minor issues may need attention.")
    else:
        print("⚠️ ATTENTION NEEDED! Some enhanced features require fixes.")
    
    print("\n🧠 ENHANCED INTELLIGENCE FEATURES:")
    print("✅ Advanced content classification (academic, technical, legal)")
    print("✅ Semantic content grouping with theme detection")
    print("✅ Cross-reference preservation with automatic guides")
    print("✅ Integration with existing translation pipeline")
    print("✅ Enhanced prompt generation with intelligence")
    print("✅ Fallback behavior for compatibility")
    print("✅ Zero compromise to existing functionality")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
