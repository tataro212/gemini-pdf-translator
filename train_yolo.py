from ultralytics import YOLO
import os

def train_custom_yolo_model():
    # Load a pre-trained YOLO model (e.g., yolov8n.pt for YOLOv8 Nano)
    # You can choose other models like yolov8s.pt, yolov8m.pt, etc.
    # The model will be downloaded automatically if not present.
    model = YOLO('yolov8n.pt')  # Or specify a model with a different architecture

    # Path to your dataset YAML file
    # IMPORTANT: Make sure this path is correct and the YAML file exists!
    dataset_yaml_path = r'C:\Users\30694\datasets\my_dataset.yaml'

    # Training parameters
    epochs = 50  # Number of training epochs
    img_size = 640  # Image size for training
    batch_size = 16 # Batch size (adjust based on your GPU memory)
    project_name = 'my_yolo_training_results' # Project directory where results are saved
    run_name = 'run1' # Name for this specific run

    print(f"Starting training with dataset: {dataset_yaml_path}")
    print(f"Epochs: {epochs}, Image Size: {img_size}, Batch Size: {batch_size}")
    print(f"Results will be saved in project: {project_name}, run: {run_name}")

    if not os.path.exists(os.path.dirname(dataset_yaml_path)):
        print(f"ERROR: The directory for the dataset YAML file does not exist: {os.path.dirname(dataset_yaml_path)}")
        print("Please ensure your dataset is correctly set up at C:\\Users\\30694\\datasets\\")
        return

    if not os.path.isfile(dataset_yaml_path):
        print(f"ERROR: Dataset YAML file not found at: {dataset_yaml_path}")
        print("Please create 'my_dataset.yaml' in C:\\Users\\30694\\datasets\\ with the correct paths and class names.")
        print("Example 'my_dataset.yaml':")
        print('''
# Train/val/test sets
path: C:/Users/30694/datasets  # dataset root dir
train: images/train  # train images (relative to 'path')
val: images/val  # val images (relative to 'path')

# Classes
names:
  0: your_class_name_0
  1: your_class_name_1
  # ... add more classes as needed
        ''')
        return

    try:
        # Train the model
        results = model.train(
            data=dataset_yaml_path,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            project=project_name,
            name=run_name
        )
        print("Training completed.")
        print(f"Results saved to: {results.save_dir}") # Access the save directory from the results

    except Exception as e:
        print(f"An error occurred during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    train_custom_yolo_model()
