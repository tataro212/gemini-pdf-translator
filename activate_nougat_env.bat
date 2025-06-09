@echo off
echo ========================================
echo   Activating Nougat Environment
echo ========================================
echo.
echo This script activates the Conda environment with:
echo - Python 3.11
echo - PyTorch 2.5.1 with CUDA 12.1 support
echo - Transformers 4.36.2 (compatible with Nougat)
echo - Tokenizers 0.15.2 (compatible with Nougat)
echo - Nougat-OCR 0.1.17
echo - All required dependencies
echo.
echo Your GPU: NVIDIA GeForce RTX 3050 Laptop GPU
echo.

REM Change to the project directory
cd /d "C:\Users\30694\gemini_translator_env"

REM Activate the conda environment
call C:\Users\30694\Miniconda3\Scripts\activate.bat nougat_env

echo Environment activated successfully!
echo.
echo You can now use Nougat with commands like:
echo   nougat path/to/document.pdf
echo.
echo Or use it in your Python scripts:
echo   from nougat import NougatModel
echo.
echo To test the installation, run:
echo   python test_nougat_conda.py
echo.

REM Keep the command prompt open
cmd /k
