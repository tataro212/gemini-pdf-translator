# YOLO Environment Replication Guide

## 🎯 Quick Setup (Recommended)

### Windows Users
1. **Double-click** `setup_yolo_environment.bat`
2. **Wait** for the installation to complete
3. **Activate** the environment: `conda activate yolo_env`
4. **Start training**: `python two_stage_yolo_training.py`

### Linux/Mac Users
1. **Make executable**: `chmod +x setup_yolo_environment.sh`
2. **Run script**: `./setup_yolo_environment.sh`
3. **Activate** the environment: `conda activate yolo_env`
4. **Start training**: `python two_stage_yolo_training.py`

---

## 📋 Manual Setup (Alternative)

### Prerequisites
- **Anaconda** or **Miniconda** installed
- **NVIDIA GPU** with CUDA support (optional but recommended)

### Step-by-Step Installation

#### 1. Create Environment
```bash
conda create -n yolo_env python=3.13 -y
conda activate yolo_env
```

#### 2. Install PyTorch with CUDA
```bash
# For CUDA 12.6 (RTX 3050)
pip install torch==2.7.1+cu126 torchvision==0.22.1+cu126 torchaudio==2.7.1+cu126 --index-url https://download.pytorch.org/whl/cu126

# For CPU only
pip install torch torchvision torchaudio
```

#### 3. Install YOLO
```bash
pip install ultralytics==8.3.155
```

#### 4. Install Additional Dependencies
```bash
pip install opencv-python==4.11.0.86 matplotlib==3.10.3 tqdm==4.67.1
```

#### 5. Install Monitoring Tools (Optional)
```bash
pip install tensorboard
```

---

## 🔧 Environment Files

### Generated Files
- `environment.yml` - Complete conda environment export
- `requirements.txt` - Complete pip requirements export
- `setup_yolo_environment.bat` - Windows setup script
- `setup_yolo_environment.sh` - Linux/Mac setup script

### Using Environment Files

#### Option 1: Conda Environment (Recommended)
```bash
# Create from environment.yml
conda env create -f environment.yml

# Activate
conda activate base  # or whatever the environment name is
```

#### Option 2: Pip Requirements
```bash
# Create new environment
conda create -n yolo_env python=3.13 -y
conda activate yolo_env

# Install from requirements.txt
pip install -r requirements.txt
```

---

## 🚀 Quick Start Commands

### Activate Environment
```bash
conda activate yolo_env  # or 'base' if using environment.yml
```

### Test Installation
```bash
python -c "import ultralytics; print(f'YOLO version: {ultralytics.__version__}')"
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Start Training
```bash
# Two-stage training (recommended)
python two_stage_yolo_training.py

# Single dataset training
python train_yolo_models.py --model n --dataset publaynet --epochs 100 --batch-size 8
```

---

## 📊 System Requirements

### Minimum
- **RAM**: 8GB
- **Storage**: 10GB free space
- **Python**: 3.10+
- **OS**: Windows 10+, Linux, macOS

### Recommended
- **GPU**: NVIDIA RTX 3050 or better
- **VRAM**: 4GB+ (for batch_size=8)
- **RAM**: 16GB
- **Storage**: 20GB free space

---

## 🔍 Troubleshooting

### Common Issues

#### 1. CUDA Not Available
```bash
# Check CUDA installation
nvidia-smi

# Install CPU-only PyTorch if needed
pip install torch torchvision torchaudio
```

#### 2. Out of Memory
- Reduce batch size: `--batch-size 4`
- Use smaller model: `--model n`
- Close other GPU applications

#### 3. Environment Conflicts
```bash
# Remove conflicting environment
conda env remove -n yolo_env

# Create fresh environment
conda create -n yolo_env python=3.13 -y
```

#### 4. Package Conflicts
```bash
# Clean install
pip uninstall ultralytics torch torchvision torchaudio -y
pip install ultralytics==8.3.155
```

---

## 📁 File Structure

After setup, your directory should look like:
```
your_project/
├── setup_yolo_environment.bat
├── setup_yolo_environment.sh
├── environment.yml
├── requirements.txt
├── two_stage_yolo_training.py
├── train_yolo_models.py
├── merged_dataset_config.yaml
├── YOLO_TRAINING_GUIDE.md
└── ENVIRONMENT_SETUP_GUIDE.md
```

---

## ✅ Verification Checklist

- [ ] Conda environment created and activated
- [ ] PyTorch installed with CUDA support
- [ ] Ultralytics YOLO installed (v8.3.155)
- [ ] OpenCV, matplotlib, tqdm installed
- [ ] GPU detected and accessible
- [ ] Training scripts copied to working directory
- [ ] Dataset YAML files configured
- [ ] Ready to start training

---

## 🎉 Success!

Once you've completed the setup, you can:

1. **Start training**: `python two_stage_yolo_training.py`
2. **Monitor progress**: Check `runs/` directory
3. **Resume training**: Re-run the same command (automatic checkpoint recovery)
4. **Use trained models**: Load `best.pt` files in your scripts

**Happy training! 🚀** 