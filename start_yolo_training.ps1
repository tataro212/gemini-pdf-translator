# Simple YOLO Training Starter Script
Write-Host "🎯 Starting YOLO Training..." -ForegroundColor Cyan

# Set environment variables for better error reporting
$env:CUDA_LAUNCH_BLOCKING = "1"
$env:TORCH_USE_CUDA_DSA = "1"

# Check GPU
Write-Host "🔍 Checking GPU..." -ForegroundColor Yellow
python -c 'import torch; print("CUDA Available:", torch.cuda.is_available()); print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")'

Write-Host ""
Write-Host "🚀 Starting training (Press Ctrl+C to stop gracefully)..." -ForegroundColor Green
Write-Host ""

# Start training
python train_yolov8_publaynet.py

Write-Host ""
Write-Host "📊 Training session completed at $(Get-Date)" -ForegroundColor Cyan
