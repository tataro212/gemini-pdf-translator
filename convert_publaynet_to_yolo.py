"""
Convert PubLayNet Dataset to YOLOv8 Format

This script converts the PubLayNet dataset from COCO format to YOLOv8 format
for fine-tuning YOLOv8 on document layout analysis.

PubLayNet Classes:
0: text
1: title  
2: list
3: table
4: figure
"""

import os
import json
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_coco_to_yolo_bbox(coco_bbox, img_width, img_height):
    """
    Convert COCO bbox format to YOLO format
    
    COCO: [x, y, width, height] (absolute coordinates)
    YOLO: [x_center, y_center, width, height] (normalized 0-1)
    """
    x, y, w, h = coco_bbox
    
    # Convert to center coordinates
    x_center = x + w / 2
    y_center = y + h / 2
    
    # Normalize by image dimensions
    x_center_norm = x_center / img_width
    y_center_norm = y_center / img_height
    w_norm = w / img_width
    h_norm = h / img_height
    
    return [x_center_norm, y_center_norm, w_norm, h_norm]

def convert_publaynet_split(publaynet_dir, split_name, output_dir):
    """Convert a single split (train/val/test) from PubLayNet to YOLO format"""
    
    logger.info(f"Converting {split_name} split...")
    
    # Paths
    images_dir = os.path.join(publaynet_dir, split_name)
    annotations_file = os.path.join(publaynet_dir, f"{split_name}.json")
    
    output_images_dir = os.path.join(output_dir, "images", split_name)
    output_labels_dir = os.path.join(output_dir, "labels", split_name)
    
    # Create output directories
    os.makedirs(output_images_dir, exist_ok=True)
    os.makedirs(output_labels_dir, exist_ok=True)
    
    # Load COCO annotations
    with open(annotations_file, 'r') as f:
        coco_data = json.load(f)
    
    # Create image ID to filename mapping
    images = {img['id']: img for img in coco_data['images']}
    
    # Group annotations by image
    annotations_by_image = {}
    for ann in coco_data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations_by_image:
            annotations_by_image[img_id] = []
        annotations_by_image[img_id].append(ann)
    
    # Convert each image and its annotations
    converted_count = 0
    
    for img_id, img_info in images.items():
        try:
            # Source image path
            src_img_path = os.path.join(images_dir, img_info['file_name'])
            
            if not os.path.exists(src_img_path):
                logger.warning(f"Image not found: {src_img_path}")
                continue
            
            # Copy image to output directory
            dst_img_path = os.path.join(output_images_dir, img_info['file_name'])
            shutil.copy2(src_img_path, dst_img_path)
            
            # Create YOLO label file
            label_filename = Path(img_info['file_name']).stem + '.txt'
            label_path = os.path.join(output_labels_dir, label_filename)
            
            # Convert annotations for this image
            yolo_annotations = []
            
            if img_id in annotations_by_image:
                for ann in annotations_by_image[img_id]:
                    # PubLayNet category mapping (already 0-indexed)
                    category_id = ann['category_id'] - 1  # Convert to 0-indexed
                    
                    # Convert bbox to YOLO format
                    yolo_bbox = convert_coco_to_yolo_bbox(
                        ann['bbox'], 
                        img_info['width'], 
                        img_info['height']
                    )
                    
                    # Create YOLO annotation line
                    yolo_line = f"{category_id} {' '.join(map(str, yolo_bbox))}"
                    yolo_annotations.append(yolo_line)
            
            # Write YOLO label file
            with open(label_path, 'w') as f:
                f.write('\n'.join(yolo_annotations))
            
            converted_count += 1
            
            if converted_count % 1000 == 0:
                logger.info(f"Converted {converted_count} images for {split_name}")
                
        except Exception as e:
            logger.error(f"Error converting image {img_info['file_name']}: {e}")
            continue
    
    logger.info(f"Completed {split_name}: {converted_count} images converted")
    return converted_count

def create_yolo_config(output_dir, publaynet_dir, has_test=False):
    """Create YOLOv8 dataset configuration file"""

    # Check what splits we actually have
    test_line = "test: images/test" if has_test else "# test: images/test  # Not available in PublayNet"

    config_content = f"""# PubLayNet Dataset Configuration for YOLOv8
# Document Layout Analysis Dataset

# Dataset path (absolute path)
path: {os.path.abspath(output_dir)}

# Train/val splits (PublayNet doesn't include test split)
train: images/train
val: images/val
{test_line}

# Number of classes
nc: 5

# Class names (PubLayNet categories)
names:
  0: text
  1: title
  2: list
  3: table
  4: figure

# Dataset info
dataset_name: PubLayNet
description: Document layout analysis dataset with 5 categories
source: https://github.com/ibm-aur-nlp/PubLayNet
note: PublayNet typically only provides train and validation splits
"""

    config_path = os.path.join(output_dir, "publaynet.yaml")
    with open(config_path, 'w') as f:
        f.write(config_content)

    logger.info(f"Created YOLOv8 config file: {config_path}")
    return config_path

def main():
    """Main conversion function"""

    # Configuration - allow command line arguments or interactive input
    import sys

    if len(sys.argv) >= 2:
        publaynet_dir = sys.argv[1]
    else:
        publaynet_dir = input("Enter path to PubLayNet dataset directory: ").strip()
        if not publaynet_dir:
            publaynet_dir = os.path.expanduser("~/datasets/publaynet")

    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        output_dir = input("Enter output directory for YOLOv8 format (default: ./publaynet_yolo): ").strip()
        if not output_dir:
            output_dir = "./publaynet_yolo"

    # Validate input directory
    if not os.path.exists(publaynet_dir):
        logger.error(f"PubLayNet directory not found: {publaynet_dir}")
        logger.info("Please download PubLayNet dataset first using:")
        logger.info("python setup_publaynet_dataset.py")
        return False

    # Check for required files (PublayNet only has train and val, no test)
    required_files = ['train.json', 'val.json']
    for file in required_files:
        if not os.path.exists(os.path.join(publaynet_dir, file)):
            logger.error(f"Required file not found: {file}")
            return

    # Check if test.json exists (optional)
    has_test = os.path.exists(os.path.join(publaynet_dir, 'test.json'))
    if not has_test:
        logger.info("ℹ️ No test.json found - PublayNet typically only provides train/val splits")

    logger.info("🚀 Starting PubLayNet to YOLOv8 conversion...")
    logger.info(f"Source: {publaynet_dir}")
    logger.info(f"Output: {output_dir}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Convert each split
    total_converted = 0

    # Available splits in PublayNet
    available_splits = ['train', 'val']
    if has_test:
        available_splits.append('test')

    for split in available_splits:
        if os.path.exists(os.path.join(publaynet_dir, split)):
            count = convert_publaynet_split(publaynet_dir, split, output_dir)
            total_converted += count
        else:
            logger.warning(f"Split directory not found: {split}")

    # Create YOLOv8 configuration file
    config_path = create_yolo_config(output_dir, publaynet_dir, has_test)

    logger.info("✅ Conversion completed!")
    logger.info(f"Total images converted: {total_converted}")
    logger.info(f"YOLOv8 dataset ready at: {output_dir}")
    logger.info(f"Config file: {config_path}")
    logger.info("\nNext steps:")
    logger.info("1. Train YOLOv8: python train_yolov8_publaynet.py")
    logger.info("2. Use config: publaynet.yaml")

    return True

if __name__ == "__main__":
    main()
