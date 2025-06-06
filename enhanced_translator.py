import re
import difflib

class DocumentStructureTranslator:
    def __init__(self, translator_service):
        self.translator = translator_service
        
    def translate_document(self, source_document):
        # Extract structural elements
        toc_entries = self.extract_toc(source_document)
        paragraphs = self.preserve_paragraphs(source_document)
        images = self.extract_image_references(source_document)
        
        # Translate content while preserving structure
        translated_toc = self.translate_toc(toc_entries)
        translated_paragraphs = self.translate_paragraphs(paragraphs)
        
        # Reconstruct document
        translated_document = self.recreate_toc(translated_toc)
        translated_document += "\n\n"
        translated_content = self.reconstruct_paragraphs(translated_paragraphs)
        translated_document += self.place_images(translated_content, images)
        
        return translated_document
    
    def extract_toc(self, document):
        toc_entries = []
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        for match in heading_pattern.finditer(document):
            level = len(match.group(1))
            text = match.group(2).strip()
            position = match.start()
            toc_entries.append({"level": level, "text": text, "position": position})
        return toc_entries
    
    def translate_toc(self, toc_entries):
        translated_entries = []
        for entry in toc_entries:
            translated_text = self.translator.translate(entry["text"])
            translated_entries.append({
                "level": entry["level"],
                "text": translated_text,
                "position": entry["position"]
            })
        return translated_entries
    
    def recreate_toc(self, translated_toc_entries):
        toc = "# Table of Contents\n\n"
        for entry in translated_toc_entries:
            indent = "  " * (entry["level"] - 1)
            slug = ''.join(e for e in entry['text'].lower() if e.isalnum() or e.isspace()).replace(' ', '-')
            toc += f"{indent}- [{entry['text']}](#{slug})\n"
        return toc
    
    def preserve_paragraphs(self, text):
        # Remove TOC and headings first to focus on content paragraphs
        content = re.sub(r'^#{1,6}\s+.+$', '', text, flags=re.MULTILINE)
        # Split by double newlines to identify paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        # Filter out empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        # Store paragraph metadata
        paragraph_data = []
        for p in paragraphs:
            # Check if paragraph contains an image
            has_image = bool(re.search(r'!\[.*?\]\(.*?\)', p))
            paragraph_data.append({
                "text": p,
                "length": len(p),
                "has_image": has_image
            })
        return paragraph_data
    
    def translate_paragraphs(self, paragraphs):
        translated = []
        for para in paragraphs:
            # Skip translation for paragraphs that are just images
            if para["has_image"] and len(re.sub(r'!\[.*?\]\(.*?\)', '', para["text"])).strip() == 0:
                translated.append(para["text"])
            else:
                # For mixed content, preserve image tags during translation
                if para["has_image"]:
                    # Replace image tags with placeholders before translation
                    placeholders = {}
                    modified_text = para["text"]
                    img_pattern = re.compile(r'(!\[.*?\]\(.*?\))')
                    for i, match in enumerate(img_pattern.finditer(para["text"])):
                        placeholder = f"__IMG_PLACEHOLDER_{i}__"
                        placeholders[placeholder] = match.group(0)
                        modified_text = modified_text.replace(match.group(0), placeholder)
                    
                    # Translate text with placeholders
                    translated_text = self.translator.translate(modified_text)
                    
                    # Restore image tags
                    for placeholder, img_tag in placeholders.items():
                        translated_text = translated_text.replace(placeholder, img_tag)
                    
                    translated.append(translated_text)
                else:
                    translated.append(self.translator.translate(para["text"]))
        return translated
    
    def reconstruct_paragraphs(self, translated_paragraphs):
        result = ""
        for para in translated_paragraphs:
            result += para + "\n\n"
        return result.strip()
    
    def extract_image_references(self, document):
        image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)', re.DOTALL)
        images = []
        for match in image_pattern.finditer(document):
            alt_text = match.group(1)
            src = match.group(2)
            # Get surrounding context (100 chars before and after)
            start_context = max(0, match.start() - 100)
            end_context = min(len(document), match.end() + 100)
            context = document[start_context:end_context]
            
            # Find the paragraph containing this image
            paragraph_start = document.rfind("\n\n", 0, match.start())
            paragraph_end = document.find("\n\n", match.end())
            if paragraph_start == -1:
                paragraph_start = 0
            if paragraph_end == -1:
                paragraph_end = len(document)
            
            paragraph_context = document[paragraph_start:paragraph_end].strip()
            
            images.append({
                "alt": alt_text,
                "src": src,
                "position": match.start(),
                "context": context,
                "paragraph_context": paragraph_context
            })
        return images
    
    def find_best_position(self, translated_text, original_context, translated_context):
        """Find the best position to insert an image based on context matching"""
        # Try to find exact paragraph match first
        if translated_context in translated_text:
            return translated_text.find(translated_context)
        
        # If no exact match, use fuzzy matching
        matches = difflib.get_close_matches(translated_context, 
                                           [translated_text[i:i+len(translated_context)+50] 
                                            for i in range(0, len(translated_text), 50)],
                                           n=1, cutoff=0.3)
        
        if matches:
            return translated_text.find(matches[0])
        
        # Fallback: try to match based on surrounding words
        words = re.findall(r'\b\w+\b', original_context)
        if words:
            # Try to find concentrations of matching words
            best_pos = 0
            max_matches = 0
            for i in range(0, len(translated_text), 20):
                chunk = translated_text[i:i+200]
                matches = sum(1 for word in words if word.lower() in chunk.lower())
                if matches > max_matches:
                    max_matches = matches
                    best_pos = i
            return best_pos
        
        # Last resort: place at the end
        return len(translated_text)
    
    def place_images(self, translated_text, image_data):
        # First translate all alt texts
        for img in image_data:
            img["translated_alt"] = self.translator.translate(img["alt"])
            if "paragraph_context" in img:
                img["translated_context"] = self.translator.translate(img["paragraph_context"])
        
        # Sort images by their original position to maintain relative order
        sorted_images = sorted(image_data, key=lambda x: x["position"])
        
        # Create a copy of the text to modify
        result = translated_text
        
        # Track offsets as we insert images
        offset = 0
        
        for img in sorted_images:
            image_tag = f'![{img["translated_alt"]}]({img["src"]})'
            
            # Check if image is already in the text (preserved during paragraph translation)
            img_pattern = re.compile(r'!\[.*?\]\(' + re.escape(img["src"]) + r'\)')
            if img_pattern.search(result):
                continue
                
            # Find the best position to insert the image
            if "translated_context" in img:
                pos = self.find_best_position(result, img["context"], img["translated_context"])
            else:
                pos = self.find_best_position(result, img["context"], "")
            
            # Adjust position based on previous insertions
            pos += offset
            
            # Insert the image
            result = result[:pos] + "\n\n" + image_tag + "\n\n" + result[pos:]
            
            # Update offset
            offset += len("\n\n" + image_tag + "\n\n")
            
        return result

# Example translator service (replace with actual translation API)
class TranslatorService:
    def translate(self, text):
        # Placeholder for actual translation service
        # Replace with your preferred translation API
        return text  # In a real implementation, this would return translated text

# Usage example
if __name__ == "__main__":
    translator_service = TranslatorService()
    document_translator = DocumentStructureTranslator(translator_service)
    
    # Example document
    sample_document = """# My Document
    
## Introduction
    
This is a sample document with multiple paragraphs.
    
![Sample Image](images/sample.jpg)
    
## Section 1
    
This is the first section with important content.
    
## Section 2
    
Another section with an embedded image: ![Another Image](images/another.png) right in the middle of text.
"""
    
    translated = document_translator.translate_document(sample_document)
    print(translated)