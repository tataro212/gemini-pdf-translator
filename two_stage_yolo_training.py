#!/usr/bin/env python3
"""
Two-Stage YOLO Training for Document Layout Analysis
Stage 1: Train on PubLayNet (5 classes) - General document understanding
Stage 2: Fine-tune on DocLayNet (8 classes) - Specialized document analysis
"""

import os
import yaml
import shutil
from pathlib import Path
from ultralytics import YOLO
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwoStageYOLOTrainer:
    def __init__(self, datasets_path="C:/Users/30694/datasets"):
        self.datasets_path = Path(datasets_path)
        self.publaynet_path = self.datasets_path / "publaynet_yolo"
        self.doclaynet_path = self.datasets_path / "doclaynet_yolo"
        self.output_path = Path("runs/two_stage_training")
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Checkpoint management
        self.checkpoint_file = self.output_path / "training_checkpoint.json"
        self.stage1_checkpoint_dir = self.output_path / "stage1_publaynet" / "yolov8_publaynet_base"
        self.stage2_checkpoint_dir = self.output_path / "stage2_doclaynet" / "yolov8_doclaynet_finetuned"
        
        # Training configurations with enhanced checkpoint settings
        self.stage1_config = {
            'model': 'yolov8n.pt',  # Start with nano model
            'data': str(self.publaynet_path / "publaynet.yaml"),
            'epochs': 100,
            'imgsz': 640,
            'batch': 8,  # Reduced from 16 to 8 for RTX 3050 4GB
            'patience': 20,
            'save': True,
            'save_period': 5,  # Save every 5 epochs (more frequent checkpoints)
            'cache': False,
            'device': '0',  # Use GPU if available
            'workers': 4,
            'project': str(self.output_path / "stage1_publaynet"),
            'name': 'yolov8_publaynet_base',
            'resume': False,  # Disable resume from checkpoint
            'exist_ok': True  # Overwrite existing runs
        }
        
        self.stage2_config = {
            'model': None,  # Will be set to stage1 best model
            'data': str(self.datasets_path / "my_dataset.yaml"),
            'epochs': 50,
            'imgsz': 640,
            'batch': 8,  # Reduced from 16 to 8 for RTX 3050 4GB
            'patience': 15,
            'save': True,
            'save_period': 3,  # Save every 3 epochs for fine-tuning
            'cache': False,
            'device': '0',
            'workers': 4,
            'project': str(self.output_path / "stage2_doclaynet"),
            'name': 'yolov8_doclaynet_finetuned',
            'resume': False,  # Disable resume from checkpoint
            'exist_ok': True,  # Overwrite existing runs
            'lr0': 0.001,  # Lower learning rate for fine-tuning
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'pose': 12.0,
            'kobj': 1.0,
            'label_smoothing': 0.0,
            'nbs': 64,
            'overlap_mask': True,
            'mask_ratio': 4,
            'dropout': 0.0,
            'val': True
        }
    
    def validate_datasets(self):
        """Validate that both datasets are properly formatted"""
        logger.info("🔍 Validating datasets...")
        
        # Check PubLayNet
        publaynet_yaml = self.publaynet_path / "publaynet.yaml"
        if not publaynet_yaml.exists():
            raise FileNotFoundError(f"PubLayNet config not found: {publaynet_yaml}")
        
        # Check DocLayNet
        doclaynet_train = self.doclaynet_path / "train"
        doclaynet_val = self.doclaynet_path / "val"
        
        if not doclaynet_train.exists() or not doclaynet_val.exists():
            raise FileNotFoundError(f"DocLayNet train/val directories not found")
        
        # Check merged dataset config
        merged_yaml = self.datasets_path / "my_dataset.yaml"
        if not merged_yaml.exists():
            raise FileNotFoundError(f"Merged dataset config not found: {merged_yaml}")
        
        logger.info("✅ All datasets validated successfully")
        return True
    
    def stage1_train_publaynet(self):
        """Stage 1: Train on PubLayNet dataset (5 classes)"""
        logger.info("🚀 Starting Stage 1: PubLayNet Training")
        logger.info(f"Training on {self.stage1_config['data']}")
        
        try:
            # Initialize model
            model = YOLO(self.stage1_config['model'])
            
            # Start training
            results = model.train(
                data=self.stage1_config['data'],
                epochs=self.stage1_config['epochs'],
                imgsz=self.stage1_config['imgsz'],
                batch=self.stage1_config['batch'],
                patience=self.stage1_config['patience'],
                save=self.stage1_config['save'],
                save_period=self.stage1_config['save_period'],
                cache=self.stage1_config['cache'],
                device=self.stage1_config['device'],
                workers=self.stage1_config['workers'],
                project=self.stage1_config['project'],
                name=self.stage1_config['name'],
                resume=self.stage1_config['resume'],
                exist_ok=self.stage1_config['exist_ok']
            )
            
            # Get best model path
            best_model_path = Path(results.save_dir) / "weights" / "best.pt"
            if best_model_path.exists():
                logger.info(f"✅ Stage 1 completed! Best model: {best_model_path}")
                return str(best_model_path)
            else:
                raise FileNotFoundError("Best model not found after training")
                
        except Exception as e:
            logger.error(f"❌ Stage 1 training failed: {e}")
            raise
    
    def stage2_finetune_doclaynet(self, stage1_model_path):
        """Stage 2: Fine-tune on DocLayNet dataset (8 classes)"""
        logger.info("🚀 Starting Stage 2: DocLayNet Fine-tuning")
        logger.info(f"Using pre-trained model: {stage1_model_path}")
        logger.info(f"Training on {self.stage2_config['data']}")
        
        try:
            # Update model path
            self.stage2_config['model'] = stage1_model_path
            
            # Initialize model with pre-trained weights
            model = YOLO(stage1_model_path)
            
            # Start fine-tuning
            results = model.train(
                data=self.stage2_config['data'],
                epochs=self.stage2_config['epochs'],
                imgsz=self.stage2_config['imgsz'],
                batch=self.stage2_config['batch'],
                patience=self.stage2_config['patience'],
                save=self.stage2_config['save'],
                save_period=self.stage2_config['save_period'],
                cache=self.stage2_config['cache'],
                device=self.stage2_config['device'],
                workers=self.stage2_config['workers'],
                project=self.stage2_config['project'],
                name=self.stage2_config['name'],
                lr0=self.stage2_config['lr0'],
                lrf=self.stage2_config['lrf'],
                momentum=self.stage2_config['momentum'],
                weight_decay=self.stage2_config['weight_decay'],
                warmup_epochs=self.stage2_config['warmup_epochs'],
                warmup_momentum=self.stage2_config['warmup_momentum'],
                warmup_bias_lr=self.stage2_config['warmup_bias_lr'],
                box=self.stage2_config['box'],
                cls=self.stage2_config['cls'],
                dfl=self.stage2_config['dfl'],
                pose=self.stage2_config['pose'],
                kobj=self.stage2_config['kobj'],
                label_smoothing=self.stage2_config['label_smoothing'],
                nbs=self.stage2_config['nbs'],
                overlap_mask=self.stage2_config['overlap_mask'],
                mask_ratio=self.stage2_config['mask_ratio'],
                dropout=self.stage2_config['dropout'],
                val=self.stage2_config['val'],
                resume=self.stage2_config['resume'],
                exist_ok=self.stage2_config['exist_ok']
            )
            
            # Get best model path
            best_model_path = Path(results.save_dir) / "weights" / "best.pt"
            if best_model_path.exists():
                logger.info(f"✅ Stage 2 completed! Final model: {best_model_path}")
                return str(best_model_path)
            else:
                raise FileNotFoundError("Best model not found after fine-tuning")
                
        except Exception as e:
            logger.error(f"❌ Stage 2 training failed: {e}")
            raise
    
    def evaluate_final_model(self, model_path):
        """Evaluate the final trained model"""
        logger.info("📊 Evaluating final model...")
        
        try:
            model = YOLO(model_path)
            
            # Evaluate on validation set
            results = model.val(
                data=self.stage2_config['data'],
                imgsz=640,
                batch=16,
                device=self.stage2_config['device']
            )
            
            logger.info("✅ Model evaluation completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            raise
    
    def run_complete_training(self):
        """Run the complete two-stage training pipeline with robust resume logic"""
        logger.info("🎯 Starting Two-Stage YOLO Training Pipeline")
        try:
            # Validate datasets
            self.validate_datasets()

            # --- Stage 1: Train on PubLayNet ---
            self.stage1_config['resume'] = self._checkpoint_exists(self.stage1_config)
            try:
                stage1_model = self.stage1_train_publaynet()
            except AssertionError as e:
                if "nothing to resume" in str(e):
                    logger.warning("Stage 1: Nothing to resume, starting fresh.")
                    self.stage1_config['resume'] = False
                    stage1_model = self.stage1_train_publaynet()
                else:
                    raise

            # --- Stage 2: Fine-tune on DocLayNet ---
            self.stage2_config['resume'] = self._checkpoint_exists(self.stage2_config)
            try:
                final_model = self.stage2_finetune_doclaynet(stage1_model)
            except AssertionError as e:
                if "nothing to resume" in str(e):
                    logger.warning("Stage 2: Nothing to resume, starting fresh.")
                    self.stage2_config['resume'] = False
                    final_model = self.stage2_finetune_doclaynet(stage1_model)
                else:
                    raise

            # Evaluate final model
            evaluation_results = self.evaluate_final_model(final_model)

            logger.info("🎉 Two-stage training completed successfully!")
            logger.info(f"Final model saved at: {final_model}")

            return {
                'stage1_model': stage1_model,
                'final_model': final_model,
                'evaluation_results': evaluation_results
            }
        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            raise

    def _checkpoint_exists(self, config):
        checkpoint_path = os.path.join(config['project'], config['name'], 'weights', 'last.pt')
        return os.path.exists(checkpoint_path)

def main():
    """Main execution function"""
    trainer = TwoStageYOLOTrainer()
    
    # Run complete training
    results = trainer.run_complete_training()
    
    print("\n" + "="*50)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print(f"Stage 1 Model: {results['stage1_model']}")
    print(f"Final Model: {results['final_model']}")
    print("="*50)

if __name__ == "__main__":
    main() 