"""
Visualization Module
Creates plots and charts for model performance and detection results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


class DetectionVisualizer:
    """Visualize detection results and model performance"""
    
    def __init__(self, output_dir='visualizations/'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_confusion_matrix(self, y_true, y_pred, save_path=None):
        """Plot confusion matrix"""
        
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Normal', 'Zombie WiFi'],
                   yticklabels=['Normal', 'Zombie WiFi'])
        
        plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Confusion matrix saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_roc_curve(self, y_true, y_proba, save_path=None):
        """Plot ROC curve"""
        
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', 
                label='Random Classifier')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('Receiver Operating Characteristic (ROC) Curve', 
                 fontsize=16, fontweight='bold')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"ROC curve saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_feature_importance(self, feature_names, importances, top_n=15, save_path=None):
        """Plot feature importance"""
        
        # Sort features by importance
        indices = np.argsort(importances)[::-1][:top_n]
        top_features = [feature_names[i] for i in indices]
        top_importances = [importances[i] for i in indices]
        
        plt.figure(figsize=(10, 8))
        colors = sns.color_palette("viridis", len(top_features))
        
        plt.barh(range(len(top_features)), top_importances, color=colors)
        plt.yticks(range(len(top_features)), top_features)
        plt.xlabel('Importance Score', fontsize=12)
        plt.ylabel('Feature', fontsize=12)
        plt.title(f'Top {top_n} Most Important Features', 
                 fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Add values on bars
        for i, v in enumerate(top_importances):
            plt.text(v + 0.001, i, f'{v:.4f}', va='center')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Feature importance plot saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_detection_timeline(self, detection_history, save_path=None):
        """Plot detection results over time"""
        
        timestamps = [r.timestamp for r in detection_history]
        alert_levels = [r.alert_level for r in detection_history]
        confidences = [r.confidence for r in detection_history]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Alert levels
        colors = {0: 'green', 1: 'blue', 2: 'yellow', 3: 'orange', 4: 'red'}
        color_map = [colors[level] for level in alert_levels]
        
        ax1.scatter(range(len(timestamps)), alert_levels, c=color_map, s=100, alpha=0.6)
        ax1.plot(range(len(timestamps)), alert_levels, 'k-', alpha=0.3)
        ax1.set_ylabel('Alert Level', fontsize=12)
        ax1.set_title('Detection Timeline', fontsize=16, fontweight='bold')
        ax1.set_yticks([0, 1, 2, 3, 4])
        ax1.set_yticklabels(['Normal', 'Low', 'Medium', 'High', 'Critical'])
        ax1.grid(True, alpha=0.3)
        
        # Confidence scores
        ax2.plot(range(len(timestamps)), confidences, 'b-', linewidth=2)
        ax2.fill_between(range(len(timestamps)), confidences, alpha=0.3)
        ax2.axhline(y=0.85, color='r', linestyle='--', label='High Confidence')
        ax2.axhline(y=0.65, color='orange', linestyle='--', label='Medium Confidence')
        ax2.set_xlabel('Detection Number', fontsize=12)
        ax2.set_ylabel('Confidence', fontsize=12)
        ax2.set_ylim([0, 1])
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Timeline plot saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_feature_distribution(self, df, feature_name, save_path=None):
        """Plot feature distribution for normal vs attack traffic"""
        
        if 'label' not in df.columns:
            print("Error: DataFrame must contain 'label' column")
            return
        
        plt.figure(figsize=(10, 6))
        
        # Separate by class
        normal = df[df['label'] == 0][feature_name]
        attack = df[df['label'] == 1][feature_name]
        
        # Plot distributions
        plt.hist(normal, bins=30, alpha=0.6, label='Normal', color='green')
        plt.hist(attack, bins=30, alpha=0.6, label='Zombie WiFi', color='red')
        
        plt.xlabel(feature_name, fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title(f'Distribution of {feature_name}', fontsize=16, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Distribution plot saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_model_comparison(self, results_dict, save_path=None):
        """Compare performance of multiple models"""
        
        if not results_dict:
            print("No results to plot")
            return
        
        # Prepare data
        models = list(results_dict.keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        data = []
        for metric in metrics:
            values = [results_dict[model].get(metric, 0) for model in models]
            data.append(values)
        
        # Plot
        x = np.arange(len(models))
        width = 0.2
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, (metric, values) in enumerate(zip(metrics, data)):
            offset = width * (i - 1.5)
            ax.bar(x + offset, values, width, label=metric.replace('_', ' ').title(), 
                  color=colors[i])
        
        ax.set_ylabel('Score', fontsize=12)
        ax.set_xlabel('Model', fontsize=12)
        ax.set_title('Model Performance Comparison', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for i, (metric, values) in enumerate(zip(metrics, data)):
            offset = width * (i - 1.5)
            for j, v in enumerate(values):
                ax.text(j + offset, v + 0.02, f'{v:.2f}', 
                       ha='center', va='bottom', fontsize=8)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison plot saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def plot_training_history(self, history, save_path=None):
        """Plot training history (for models that support it)"""
        
        if 'train_loss' not in history or 'val_loss' not in history:
            print("Training history not available")
            return
        
        epochs = range(1, len(history['train_loss']) + 1)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss
        ax1.plot(epochs, history['train_loss'], 'b-', label='Training Loss')
        ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss')
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.set_title('Model Loss', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Accuracy
        ax2.plot(epochs, history['train_acc'], 'b-', label='Training Accuracy')
        ax2.plot(epochs, history['val_acc'], 'r-', label='Validation Accuracy')
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Accuracy', fontsize=12)
        ax2.set_title('Model Accuracy', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training history saved to {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def create_dashboard(self, model, X_test, y_test, feature_names):
        """Create comprehensive dashboard with multiple plots"""
        
        # Predictions
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Confusion Matrix
        ax1 = fig.add_subplot(gs[0, 0])
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1,
                   xticklabels=['Normal', 'Zombie WiFi'],
                   yticklabels=['Normal', 'Zombie WiFi'])
        ax1.set_title('Confusion Matrix', fontweight='bold')
        
        # 2. ROC Curve
        ax2 = fig.add_subplot(gs[0, 1])
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        ax2.plot(fpr, tpr, 'b-', linewidth=2, label=f'AUC = {roc_auc:.3f}')
        ax2.plot([0, 1], [0, 1], 'r--')
        ax2.set_xlabel('False Positive Rate')
        ax2.set_ylabel('True Positive Rate')
        ax2.set_title('ROC Curve', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Feature Importance
        ax3 = fig.add_subplot(gs[1, :])
        importances = model.model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]
        ax3.barh(range(10), importances[indices], color='steelblue')
        ax3.set_yticks(range(10))
        ax3.set_yticklabels([feature_names[i] for i in indices])
        ax3.set_xlabel('Importance')
        ax3.set_title('Top 10 Feature Importances', fontweight='bold')
        ax3.invert_yaxis()
        
        # 4. Prediction Distribution
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.hist(y_proba[y_test == 0], bins=20, alpha=0.6, label='Normal', color='green')
        ax4.hist(y_proba[y_test == 1], bins=20, alpha=0.6, label='Attack', color='red')
        ax4.set_xlabel('Prediction Probability')
        ax4.set_ylabel('Count')
        ax4.set_title('Prediction Distribution', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Metrics Summary
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis('off')
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        metrics_text = f"""
        PERFORMANCE METRICS
        
        Accuracy:  {accuracy_score(y_test, y_pred):.3f}
        Precision: {precision_score(y_test, y_pred):.3f}
        Recall:    {recall_score(y_test, y_pred):.3f}
        F1-Score:  {f1_score(y_test, y_pred):.3f}
        AUC-ROC:   {roc_auc:.3f}
        
        Test Samples: {len(y_test)}
        True Positives:  {cm[1,1]}
        True Negatives:  {cm[0,0]}
        False Positives: {cm[0,1]}
        False Negatives: {cm[1,0]}
        """
        
        ax5.text(0.1, 0.5, metrics_text, fontsize=12, family='monospace',
                verticalalignment='center')
        
        plt.suptitle('Zombie WiFi Detection - Model Dashboard', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        # Save
        save_path = os.path.join(self.output_dir, 'dashboard.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nDashboard saved to {save_path}")
        
        plt.show()


if __name__ == "__main__":
    print("=== Visualization Module ===")
    print("This module provides visualization functions for:")
    print("  • Confusion matrices")
    print("  • ROC curves")
    print("  • Feature importance")
    print("  • Detection timelines")
    print("  • Model comparisons")
    print("  • Comprehensive dashboards")
