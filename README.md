# Gemini PDF Translator

A comprehensive PDF translation system powered by Google's Gemini AI, featuring advanced visual content extraction with Nougat integration, intelligent document processing, and high-quality translation capabilities.

## 🚀 Features

### Core Translation Capabilities
- **Multi-language PDF translation** using Google Gemini AI
- **Smart content grouping** for optimized API usage
- **Advanced caching system** to avoid redundant translations
- **Intelligent text extraction** with layout preservation
- **Table of Contents (TOC) extraction** and translation

### Visual Content Processing
- **Nougat integration** for advanced visual content extraction
- **Mathematical equations** recognition and processing
- **Scientific diagrams** and complex tables handling
- **Image classification** and smart filtering
- **Vector graphics** and raster image processing

### Document Intelligence
- **Automatic document structure analysis**
- **Smart subtitle classification**
- **Content quality optimization**
- **Placeholder-based translation** for complex layouts
- **Enhanced document formatting** preservation

### Advanced Features
- **Modular architecture** for easy customization
- **Comprehensive error handling** with graceful fallbacks
- **Real-time progress tracking** and logging
- **Google Drive integration** for output management
- **Visual inspection tools** for quality assurance

## 📋 Requirements

### Python Dependencies
```
python>=3.11
google-generativeai
PyMuPDF (fitz)
Pillow
python-docx
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
configparser
```

### Optional Dependencies (for enhanced features)
```
nougat-ocr==0.1.17
transformers==4.45.0
tokenizers==0.20.3
torch>=2.0.0
timm==0.5.4
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gemini-pdf-translator.git
cd gemini-pdf-translator
```

### 2. Create Virtual Environment
```bash
python -m venv gemini_translator_env
source gemini_translator_env/bin/activate  # On Windows: gemini_translator_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Nougat (Optional - for advanced visual processing)
```bash
# If you have Rust installed:
pip install nougat-ocr==0.1.17

# Or use the automated installer:
python final_nougat_solution.py
```

### 5. Configure API Keys
1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create `config.ini` file:
```ini
[Gemini]
api_key = your_gemini_api_key_here
model_name = models/gemini-1.5-pro

[General]
target_language = Greek
nougat_only_mode = False

[Optimization]
enable_smart_grouping = True
max_group_size_chars = 8000
```

## 🚀 Quick Start

### Basic Usage
```python
from main_workflow import UltimatePDFTranslator

# Initialize translator
translator = UltimatePDFTranslator()

# Translate a PDF
translator.translate_pdf("document.pdf", "output_folder")
```

### Command Line Usage
```bash
python main_workflow.py
```

## 📖 Usage Examples

### 1. Simple Translation
```python
from main_workflow import UltimatePDFTranslator

translator = UltimatePDFTranslator()
translator.translate_pdf("research_paper.pdf", "translated_output")
```

### 2. With Nougat Enhancement
```python
from config_manager import config_manager

# Enable Nougat for advanced visual processing
config_manager.set_config_value('General', 'nougat_only_mode', True, bool)

translator = UltimatePDFTranslator()
translator.translate_pdf("scientific_document.pdf", "enhanced_output")
```

### 3. Batch Processing
```python
import os
from main_workflow import UltimatePDFTranslator

translator = UltimatePDFTranslator()

# Process all PDFs in a directory
pdf_directory = "input_pdfs"
for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, filename)
        output_folder = f"output_{filename[:-4]}"
        translator.translate_pdf(pdf_path, output_folder)
```

## 🔧 Configuration

### Main Configuration File (`config.ini`)
```ini
[Gemini]
api_key = your_api_key
model_name = models/gemini-1.5-pro
temperature = 0.1
max_tokens = 8192

[General]
target_language = Greek
source_language = auto
nougat_only_mode = False
enable_drive_upload = False

[Optimization]
enable_smart_grouping = True
max_group_size_chars = 8000
enable_caching = True
cache_expiry_days = 30

[Image_Processing]
extract_images = True
min_image_size = 100
max_image_size = 2000
image_quality_threshold = 0.7
```

## 🏗️ Architecture

### Core Components
- **`main_workflow.py`** - Main translation orchestrator
- **`pdf_parser.py`** - PDF content extraction and processing
- **`translation_service.py`** - Gemini AI integration
- **`nougat_integration.py`** - Advanced visual content processing
- **`optimization_manager.py`** - Smart content grouping and optimization
- **`config_manager.py`** - Configuration management

### Processing Pipeline
1. **PDF Analysis** - Document structure and content analysis
2. **Content Extraction** - Text, images, and visual elements
3. **Visual Processing** - Nougat-enhanced diagram and equation recognition
4. **Content Optimization** - Smart grouping for efficient translation
5. **Translation** - Gemini AI-powered translation with context preservation
6. **Document Generation** - Formatted output with preserved layout
7. **Quality Assurance** - Validation and error checking

## 🔍 Advanced Features

### Nougat Integration
- Mathematical equation recognition
- Scientific diagram processing
- Complex table extraction
- Academic document optimization

### Smart Content Processing
- Automatic subtitle classification
- Intelligent image filtering
- Context-aware translation grouping
- Layout preservation algorithms

### Quality Assurance
- Visual inspection tools
- Translation validation
- Error detection and correction
- Progress monitoring and logging

## 🐛 Troubleshooting

### Common Issues

#### Nougat Installation Problems
```bash
# Run the automated fix
python final_nougat_solution.py

# Manual installation with Rust
# Install Rust from https://rustup.rs/
pip install tokenizers==0.15.2 transformers==4.36.2 nougat-ocr==0.1.17
```

#### API Rate Limits
- Enable smart grouping in configuration
- Adjust `max_group_size_chars` to optimize API usage
- Use caching to avoid redundant translations

#### Memory Issues
- Reduce image processing quality settings
- Enable content chunking for large documents
- Close unnecessary applications during processing

## 📚 Documentation

- [Quick Start Guide](QUICK_START_GUIDE.md)
- [Nougat Integration Guide](NOUGAT_INTEGRATION_GUIDE.md)
- [Configuration Reference](config_reference.md)
- [API Documentation](api_docs.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for translation capabilities
- Nougat team for visual content extraction
- PyMuPDF for PDF processing
- The open-source community for various tools and libraries

## 📞 Support

- Create an issue for bug reports or feature requests
- Check the [troubleshooting guide](troubleshooting.md) for common problems
- Review existing issues before creating new ones

---

**Made with ❤️ for the research and academic community**
