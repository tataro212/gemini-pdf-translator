import sys

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python sys.path: {sys.path}")

try:
    from PIL import Image, __version__ as pillow_version
    print(f"Pillow version: {pillow_version} - Successfully imported!")
except ImportError as e:
    print(f"Pillow (PIL) import error: {e}")

try:
    import pytesseract
    print(f"pytesseract version: {pytesseract.get_tesseract_version()} - Successfully imported!")
    print(f"pytesseract.pytesseract.tesseract_cmd: '{pytesseract.pytesseract.tesseract_cmd}'")
    try:
        # Attempt a simple OCR operation to see if tesseract is callable
        langs = pytesseract.get_languages(config='')
        print(f"Tesseract available languages: {langs}")
        print("Tesseract engine appears to be callable by pytesseract.")
    except pytesseract.TesseractNotFoundError:
        print("Pytesseract TesseractNotFoundError: Tesseract is not installed or not in your PATH.")
        print("You may need to install Tesseract OCR engine separately and/or tell pytesseract where to find it.")
        print("For example, in your script: pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' (adjust path as needed)")
    except Exception as e:
        print(f"Error when trying to use pytesseract (e.g., Tesseract not found or other config issue): {e}")
except ImportError as e:
    print(f"pytesseract import error: {e}")
except Exception as e:
    print(f"An unexpected error occurred with pytesseract: {e}")
