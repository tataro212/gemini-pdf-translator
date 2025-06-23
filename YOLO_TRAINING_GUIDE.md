# YOLO Training Guide for Document Layout Analysis

## Current Setup Analysis

✅ **YOLO Version**: v8.3.155 (Latest stable version)  
✅ **Datasets**: DocLayNet + PubLayNet available  
✅ **Environment**: Ready for training  

## YOLO Version Recommendation

**Stick with YOLO v8.3.155** - Here's why:
- ✅ **Stable & Production Ready**: Fully tested and optimized
- ✅ **Excellent Performance**: State-of-the-art results
- ✅ **Good Documentation**: Extensive guides and examples
- ✅ **Community Support**: Large user base and active development
- ❌ **YOLO v10**: Still in alpha/development, not recommended for production

## Dataset Overview

### PubLayNet (5 classes)
- **Classes**: text, title, list, table, figure
- **Size**: ~335K document images
- **Use**: General document understanding

### DocLayNet (8 classes)  
- **Classes**: caption, footnote, formula, list-item, page-footer, page-header, picture, section-header, table, text, title
- **Size**: ~80K document images
- **Use**: Specialized document analysis

## Training Strategies

### Option 1: Two-Stage Training (Recommended)

**Stage 1**: Train on PubLayNet (5 classes)
```bash
python two_stage_yolo_training.py
```

**Stage 2**: Fine-tune on DocLayNet (8 classes)
- Uses Stage 1 model as pre-trained weights
- Lower learning rate for fine-tuning
- Better final performance

### Option 2: Single-Stage Training

**Train on PubLayNet only:**
```bash
python train_yolo_models.py --model n --dataset publaynet --epochs 100
```

**Train on DocLayNet only:**
```bash
python train_yolo_models.py --model n --dataset doclaynet --epochs 100
```

**Train on merged dataset:**
```bash
python train_yolo_models.py --model n --dataset merged --epochs 100
```

## Model Size Comparison

| Model | Parameters | Speed | Accuracy | Use Case |
|-------|------------|-------|----------|----------|
| YOLO-n | 3.2M | Fastest | Good | Quick prototyping |
| YOLO-s | 11.2M | Fast | Better | Balanced performance |
| YOLO-m | 25.9M | Medium | Best | Production use |
| YOLO-l | 43.7M | Slow | Excellent | High accuracy needed |
| YOLO-x | 68.2M | Slowest | Best | Maximum accuracy |

## Quick Start Commands

### 1. Test with Nano Model (Fastest)
```bash
# Train on PubLayNet
python train_yolo_models.py --model n --dataset publaynet --epochs 50 --batch-size 16

# Train on DocLayNet  
python train_yolo_models.py --model n --dataset doclaynet --epochs 50 --batch-size 16
```

### 2. Production Training (Medium Model)
```bash
# Two-stage training (recommended)
python two_stage_yolo_training.py

# Or single-stage on merged dataset
python train_yolo_models.py --model m --dataset merged --epochs 100 --batch-size 8
```

### 3. Compare All Models
```bash
python train_yolo_models.py --compare
```

## Hardware Requirements

### Minimum (CPU Training)
- **RAM**: 8GB
- **Storage**: 10GB free space
- **Time**: 2-4 hours per model

### Recommended (GPU Training)
- **GPU**: NVIDIA GTX 1060 or better
- **VRAM**: 6GB+ for batch size 16
- **RAM**: 16GB
- **Storage**: 20GB free space
- **Time**: 30-60 minutes per model

## Training Configuration

### Batch Size Guidelines for RTX 3050 4GB
- **YOLO-n (nano)**: batch_size = 8-12 (leaves ~1GB free)
- **YOLO-s (small)**: batch_size = 6-8 (leaves ~1GB free)  
- **YOLO-m (medium)**: batch_size = 4-6 (leaves ~1GB free)
- **YOLO-l (large)**: batch_size = 2-4 (leaves ~1GB free)
- **YOLO-x (xlarge)**: batch_size = 1-2 (leaves ~1GB free)
- **CPU only**: batch_size = 4

### Recommended Settings for Your RTX 3050
- **Quick Testing**: YOLO-n with batch_size = 8
- **Production**: YOLO-s with batch_size = 6
- **Best Accuracy**: YOLO-m with batch_size = 4

### Learning Rate
- **Stage 1**: 0.01 (default)
- **Stage 2**: 0.001 (fine-tuning)
- **Single-stage**: 0.01

## Expected Results

### PubLayNet Training (5 classes)
- **mAP@0.5**: 0.85-0.92
- **mAP@0.5:0.95**: 0.65-0.75
- **Training time**: 1-3 hours

### DocLayNet Training (8 classes)
- **mAP@0.5**: 0.80-0.88
- **mAP@0.5:0.95**: 0.60-0.70
- **Training time**: 2-4 hours

### Two-Stage Training
- **mAP@0.5**: 0.88-0.94
- **mAP@0.5:0.95**: 0.70-0.80
- **Training time**: 3-6 hours

## Monitoring Training

### TensorBoard (Optional)
```bash
# Install tensorboard
pip install tensorboard

# Start tensorboard
tensorboard --logdir runs/
```

### Training Logs
- Check `runs/train_*/` directories
- Look for `results.png` for training curves
- Check `weights/best.pt` for best model

## Model Evaluation

### Validate Trained Model
```python
from ultralytics import YOLO

# Load trained model
model = YOLO('runs/train_yolo*/weights/best.pt')

# Validate on test set
results = model.val()
```

### Test on Sample Images
```python
# Predict on single image
results = model('path/to/test/image.jpg')

# Show results
results[0].show()
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size
   - Use smaller model (nano/small)
   - Reduce image size

2. **Training Too Slow**
   - Use GPU if available
   - Reduce image size
   - Use smaller model

3. **Poor Accuracy**
   - Increase training epochs
   - Use larger model
   - Check dataset quality
   - Try two-stage training

4. **Dataset Issues**
   - Verify YAML file paths
   - Check image/label format
   - Validate class mappings

## Next Steps

1. **Start with nano model** for quick testing
2. **Use two-stage training** for best results
3. **Experiment with model sizes** based on your needs
4. **Monitor training progress** and adjust parameters
5. **Evaluate on your specific documents**

## Support

- **YOLO Documentation**: https://docs.ultralytics.com/
- **Ultralytics GitHub**: https://github.com/ultralytics/ultralytics
- **Community Forum**: https://github.com/ultralytics/ultralytics/discussions 