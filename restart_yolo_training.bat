@echo off
echo 🎯 YOLO Training Restart Script
echo ================================

REM Check if we're in the correct directory
if not exist "train_yolov8_publaynet.py" (
    echo ❌ Error: train_yolov8_publaynet.py not found in current directory
    echo Please navigate to the gemini_translator_env directory first
    pause
    exit /b 1
)

REM Check if dataset exists
if not exist "..\datasets\publaynet_yolo\publaynet.yaml" (
    echo ❌ Error: PubLayNet dataset not found
    echo Please run: python convert_publaynet_to_yolo.py first
    pause
    exit /b 1
)

echo 🔍 Checking GPU availability...
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

echo.
echo 🚀 Starting YOLO training...
echo Press Ctrl+C to stop training gracefully
echo.

REM Set environment variables for better error handling
set CUDA_LAUNCH_BLOCKING=1
set TORCH_USE_CUDA_DSA=1

REM Start training
python train_yolov8_publaynet.py

echo.
echo 📊 Training session ended at %date% %time%

REM Check if model was saved
if exist "models\yolov8_publaynet_finetuned.pt" (
    echo ✅ Final model saved: models\yolov8_publaynet_finetuned.pt
)

echo.
echo Next steps:
echo 1. Check training logs in the publaynet_training directory
echo 2. If training completed, test the model with: python test_yolov8_integration.py
echo 3. If training failed, check GPU memory and reduce batch size if needed

pause
