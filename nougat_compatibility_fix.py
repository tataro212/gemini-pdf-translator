"""
Nougat Compatibility Fix

This script patches the Nougat library to work with newer versions of transformers
by fixing the cache_position argument issue.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

def patch_nougat_model():
    """
    Patch the Nougat model to fix compatibility with newer transformers
    """
    try:
        # Find the nougat model.py file
        import nougat
        nougat_path = os.path.dirname(nougat.__file__)
        model_file = os.path.join(nougat_path, 'model.py')
        
        if not os.path.exists(model_file):
            logger.error(f"Nougat model.py not found at {model_file}")
            return False
        
        # Read the current content
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already patched
        if 'cache_position_fix_applied' in content:
            logger.info("✅ Nougat compatibility patch already applied")
            return True
        
        # Apply the patch
        # Find the problematic line and fix it
        old_code = """decoder_output = self.decoder.model.generate(
        encoder_outputs=encoder_outputs,
        attention_mask=attention_mask,
        max_length=self.config.max_length,
        early_stopping=early_stopping,
        pad_token_id=self.decoder.tokenizer.pad_token_id,
        eos_token_id=self.decoder.tokenizer.eos_token_id,
        use_cache=True,
        bad_words_ids=bad_words_ids,
        return_dict_in_generate=True,
        output_scores=True,
        output_attentions=False,
        do_sample=False,
        repetition_penalty=repetition_penalty,
        length_penalty=length_penalty,
    )"""
        
        new_code = """# cache_position_fix_applied
        # Remove cache_position from model_kwargs if present
        generate_kwargs = {
            'encoder_outputs': encoder_outputs,
            'attention_mask': attention_mask,
            'max_length': self.config.max_length,
            'early_stopping': early_stopping,
            'pad_token_id': self.decoder.tokenizer.pad_token_id,
            'eos_token_id': self.decoder.tokenizer.eos_token_id,
            'use_cache': True,
            'bad_words_ids': bad_words_ids,
            'return_dict_in_generate': True,
            'output_scores': True,
            'output_attentions': False,
            'do_sample': False,
            'repetition_penalty': repetition_penalty,
            'length_penalty': length_penalty,
        }
        
        decoder_output = self.decoder.model.generate(**generate_kwargs)"""
        
        # Replace the problematic code
        if old_code in content:
            content = content.replace(old_code, new_code)
            logger.info("✅ Applied generate() method patch")
        else:
            # Try a more targeted approach
            logger.warning("⚠️ Could not find exact match, applying alternative patch")
            # Add a compatibility wrapper
            patch_code = """
# cache_position_fix_applied - Compatibility patch for newer transformers
import functools

def _patch_generate_method(original_generate):
    @functools.wraps(original_generate)
    def patched_generate(*args, **kwargs):
        # Remove problematic cache_position argument
        kwargs.pop('cache_position', None)
        return original_generate(*args, **kwargs)
    return patched_generate

# Apply the patch to the decoder model
if hasattr(self.decoder.model, 'generate'):
    self.decoder.model.generate = _patch_generate_method(self.decoder.model.generate)
"""
            
            # Insert the patch before the inference method
            inference_method_start = content.find('def inference(')
            if inference_method_start != -1:
                content = content[:inference_method_start] + patch_code + content[inference_method_start:]
                logger.info("✅ Applied alternative compatibility patch")
            else:
                logger.error("❌ Could not find inference method to patch")
                return False
        
        # Write the patched content back
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("✅ Nougat compatibility patch applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error applying Nougat patch: {e}")
        return False

def create_nougat_wrapper():
    """
    Create a wrapper script that applies the patch and then runs Nougat
    """
    wrapper_script = '''
"""
Nougat Wrapper with Compatibility Fix
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Apply compatibility patch
        from nougat_compatibility_fix import patch_nougat_model
        patch_nougat_model()
        
        # Import and run Nougat
        from nougat_integration import NougatIntegration
        
        # Test basic functionality
        nougat = NougatIntegration()
        print("✅ Nougat wrapper initialized successfully")
        
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            output_dir = sys.argv[2] if len(sys.argv) > 2 else "nougat_output"
            
            print(f"🔍 Processing PDF: {pdf_path}")
            result = nougat.parse_pdf_with_fallback(pdf_path, output_dir)
            
            if result:
                print("✅ PDF processing completed successfully")
                print(f"📊 Found {len(result.get('mathematical_equations', []))} equations")
                print(f"📋 Found {len(result.get('tables', []))} tables")
                print(f"📑 Found {len(result.get('sections', []))} sections")
            else:
                print("❌ PDF processing failed")
        else:
            print("Usage: python nougat_wrapper.py <pdf_path> [output_dir]")
            
    except Exception as e:
        print(f"❌ Error in Nougat wrapper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open('nougat_wrapper.py', 'w', encoding='utf-8') as f:
        f.write(wrapper_script)
    
    logger.info("✅ Created nougat_wrapper.py")

def main():
    """Main function to apply all fixes"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🔧 NOUGAT COMPATIBILITY FIX")
    print("=" * 40)
    
    # Apply the patch
    if patch_nougat_model():
        print("✅ Nougat compatibility patch applied")
    else:
        print("❌ Failed to apply Nougat compatibility patch")
        return False
    
    # Create wrapper
    create_nougat_wrapper()
    print("✅ Nougat wrapper created")
    
    print("\n💡 USAGE:")
    print("1. Use: python nougat_wrapper.py <pdf_path>")
    print("2. Or use the NougatIntegration class directly")
    
    return True

if __name__ == "__main__":
    main()
