import os
import numpy as np
import pandas as pd
from PIL import Image
import cv2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle

def extract_image_features(image_path):
    """Extract features from an image file"""
    try:
        # Load image
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        features = {}
        
        # Image dimensions
        features['width'] = image.width
        features['height'] = image.height
        features['aspect_ratio'] = image.width / image.height
        
        # Color analysis
        mean_color = img_array.mean(axis=(0, 1))
        features['red_intensity'] = float(mean_color[0])
        features['green_intensity'] = float(mean_color[1])
        features['blue_intensity'] = float(mean_color[2])
        
        # Brightness
        features['brightness'] = float(img_array.mean())
        
        # Text density estimation (using edge detection)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        features['text_density'] = float(edges.sum() / (image.width * image.height))
        
        # Color variance
        features['color_variance'] = float(np.var(img_array))
        
        # Color saturation
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        features['saturation'] = float(hsv[:,:,1].mean())
        
        return features
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def prepare_dataset(scam_dir, legitimate_dir):
    """Prepare training dataset from image directories"""
    features_list = []
    labels = []
    
    # Process scam images
    print("Processing scam images...")
    if os.path.exists(scam_dir):
        for img_file in os.listdir(scam_dir):
            img_path = os.path.join(scam_dir, img_file)
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                features = extract_image_features(img_path)
                if features:
                    features_list.append(features)
                    labels.append(1)  # 1 = scam
    
    # Process legitimate images
    print("Processing legitimate images...")
    if os.path.exists(legitimate_dir):
        for img_file in os.listdir(legitimate_dir):
            img_path = os.path.join(legitimate_dir, img_file)
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                features = extract_image_features(img_path)
                if features:
                    features_list.append(features)
                    labels.append(0)  # 0 = legitimate
    
    # Convert to DataFrame
    df = pd.DataFrame(features_list)
    
    print(f"\nDataset prepared: {len(df)} images")
    print(f"Scam images: {sum(labels)}")
    print(f"Legitimate images: {len(labels) - sum(labels)}")
    
    return df, labels

def train_model(X, y):
    """Train the image scam detection model"""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_acc = model.score(X_train_scaled, y_train)
    test_acc = model.score(X_test_scaled, y_test)
    
    print(f"Training Accuracy: {train_acc:.3f}")
    print(f"Test Accuracy: {test_acc:.3f}")
    
    # Feature importance
    print("\nTop 5 Important Features:")
    importances = model.feature_importances_
    feature_names = X.columns
    top_features = sorted(zip(importances, feature_names), reverse=True)[:5]
    for importance, feature in top_features:
        print(f"{feature}: {importance:.4f}")
    
    return model, scaler

def main():
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Define dataset directories
    scam_dir = "../datasets/scam_images"
    legitimate_dir = "../datasets/legitimate_images"
    
    # Check if directories exist
    if not os.path.exists(scam_dir) or not os.path.exists(legitimate_dir):
        print("Error: Image dataset directories not found!")
        print(f"Please create these directories and add images:")
        print(f"  - {scam_dir} (for scam/phishing images)")
        print(f"  - {legitimate_dir} (for legitimate images)")
        print("\nCreating sample synthetic dataset for demonstration...")
        
        # Create synthetic dataset for demonstration
        X_synthetic, y_synthetic = create_synthetic_dataset()
        model, scaler = train_model(X_synthetic, y_synthetic)
    else:
        # Prepare dataset from images
        X, y = prepare_dataset(scam_dir, legitimate_dir)
        
        if len(X) < 10:
            print("Warning: Not enough images. Creating synthetic dataset...")
            X_synthetic, y_synthetic = create_synthetic_dataset()
            model, scaler = train_model(X_synthetic, y_synthetic)
        else:
            model, scaler = train_model(X, y)
    
    # Save model
    with open("models/image_scam_model.pkl", "wb") as f:
        pickle.dump((model, scaler), f)
    
    print("\nImage scam detection model saved successfully!")

def create_synthetic_dataset():
    """Create synthetic dataset for demonstration"""
    print("Creating synthetic dataset...")
    np.random.seed(42)
    
    # Generate synthetic features
    n_scam = 100
    n_legit = 100
    
    features_list = []
    labels = []
    
    # Scam images - typically have high red, high text density, unusual dimensions
    for _ in range(n_scam):
        features_list.append({
            'width': np.random.randint(300, 800),
            'height': np.random.randint(400, 1000),
            'aspect_ratio': np.random.uniform(0.3, 2.5),
            'red_intensity': np.random.uniform(120, 220),
            'green_intensity': np.random.uniform(50, 150),
            'blue_intensity': np.random.uniform(50, 150),
            'brightness': np.random.uniform(80, 180),
            'text_density': np.random.uniform(0.25, 0.5),
            'color_variance': np.random.uniform(4000, 8000),
            'saturation': np.random.uniform(100, 200)
        })
        labels.append(1)
    
    # Legitimate images - balanced colors, normal dimensions
    for _ in range(n_legit):
        features_list.append({
            'width': np.random.randint(500, 1200),
            'height': np.random.randint(500, 1200),
            'aspect_ratio': np.random.uniform(0.8, 1.5),
            'red_intensity': np.random.uniform(80, 150),
            'green_intensity': np.random.uniform(80, 150),
            'blue_intensity': np.random.uniform(80, 150),
            'brightness': np.random.uniform(100, 160),
            'text_density': np.random.uniform(0.05, 0.2),
            'color_variance': np.random.uniform(2000, 5000),
            'saturation': np.random.uniform(50, 120)
        })
        labels.append(0)
    
    df = pd.DataFrame(features_list)
    print(f"Synthetic dataset created: {len(df)} images")
    
    return df, labels

if __name__ == "__main__":
    main()
