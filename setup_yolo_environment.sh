#!/bin/bash

echo "========================================"
echo "YOLO Training Environment Setup"
echo "========================================"
echo

echo "Step 1: Creating conda environment..."
conda create -n yolo_env python=3.13 -y

echo
echo "Step 2: Activating environment..."
source activate yolo_env

echo
echo "Step 3: Installing PyTorch with CUDA..."
pip install torch==2.7.1+cu126 torchvision==0.22.1+cu126 torchaudio==2.7.1+cu126 --index-url https://download.pytorch.org/whl/cu126

echo
echo "Step 4: Installing Ultralytics YOLO..."
pip install ultralytics==8.3.155

echo
echo "Step 5: Installing additional dependencies..."
pip install opencv-python==4.11.0.86 matplotlib==3.10.3 tqdm==4.67.1

echo
echo "Step 6: Installing optional monitoring tools..."
pip install tensorboard

echo
echo "========================================"
echo "Environment Setup Complete!"
echo "========================================"
echo
echo "To activate the environment, run:"
echo "conda activate yolo_env"
echo
echo "To start training, run:"
echo "python two_stage_yolo_training.py" 