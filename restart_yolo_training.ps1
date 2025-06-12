# PowerShell Script to Restart YOLO Training with Error Handling
# This script safely restarts the YOLO training with proper error handling

Write-Host "🎯 YOLO Training Restart Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if we're in the correct directory
if (-not (Test-Path "train_yolov8_publaynet.py")) {
    Write-Host "❌ Error: train_yolov8_publaynet.py not found in current directory" -ForegroundColor Red
    Write-Host "Please navigate to the gemini_translator_env directory first" -ForegroundColor Yellow
    exit 1
}

# Check if dataset exists
if (-not (Test-Path "../datasets/publaynet_yolo/publaynet.yaml")) {
    Write-Host "❌ Error: PubLayNet dataset not found" -ForegroundColor Red
    Write-Host "Please run: python convert_publaynet_to_yolo.py first" -ForegroundColor Yellow
    exit 1
}

# Check GPU availability
Write-Host "🔍 Checking GPU availability..." -ForegroundColor Yellow
python -c 'import torch; print("CUDA Available:", torch.cuda.is_available()); print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")'

# Check for existing training runs
if (Test-Path "publaynet_training") {
    $trainingDirs = Get-ChildItem -Path "publaynet_training" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "yolov8_publaynet_finetuned*" }
    if ($trainingDirs) {
        Write-Host "📁 Found existing training runs:" -ForegroundColor Green
        foreach ($dir in $trainingDirs) {
            $checkpointPath = Join-Path $dir.FullName "weights\last.pt"
            $hasCheckpoint = Test-Path $checkpointPath
            $status = if ($hasCheckpoint) { "✅ Has checkpoint" } else { "❌ No checkpoint" }
            Write-Host "   • $($dir.Name): $status" -ForegroundColor White
        }

        Write-Host ""
        $resume = Read-Host "Do you want to resume from the latest checkpoint? (y/n)"
        if ($resume -eq "y" -or $resume -eq "Y") {
            Write-Host "🔄 Will attempt to resume training from checkpoint" -ForegroundColor Green
        }
    }
}

# Set environment variables for better error handling
$env:CUDA_LAUNCH_BLOCKING = "1"  # Better CUDA error reporting
$env:TORCH_USE_CUDA_DSA = "1"    # CUDA device-side assertions

Write-Host ""
Write-Host "🚀 Starting YOLO training..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop training gracefully" -ForegroundColor Yellow
Write-Host ""

# Start training with error handling
try {
    python train_yolov8_publaynet.py
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✅ Training completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Training failed with exit code: $exitCode" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Training script crashed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Training session ended at $(Get-Date)" -ForegroundColor Cyan

# Check if any models were saved
if (Test-Path "models\yolov8_publaynet_finetuned.pt") {
    Write-Host "✅ Final model saved: models\yolov8_publaynet_finetuned.pt" -ForegroundColor Green
}

# Show latest training results
if (Test-Path "publaynet_training") {
    $latestTraining = Get-ChildItem -Path "publaynet_training" -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "yolov8_publaynet_finetuned*" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($latestTraining) {
        Write-Host "📁 Latest training results: $($latestTraining.FullName)" -ForegroundColor Green

        # Check for results files
        $resultsFile = Join-Path $latestTraining.FullName "results.csv"
        if (Test-Path $resultsFile) {
            Write-Host "📈 Training metrics saved to: $resultsFile" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Check training logs in the publaynet_training directory" -ForegroundColor White
Write-Host "2. If training completed, test the model with: python test_yolov8_integration.py" -ForegroundColor White
Write-Host "3. If training failed, check GPU memory and reduce batch size if needed" -ForegroundColor White
