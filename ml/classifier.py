"""
Image Classifier for Shelf Inventory
Module 4, Section 2: Machine Learning

This module provides a simple image classification pipeline
to detect which items are present on a shelf.

Note: This is a demonstration classifier using simulated predictions.
In production, you would train on actual shelf images.
"""

import json
import os
import random
from datetime import datetime

# Known inventory items (from our system)
KNOWN_ITEMS = [
    "Arduino Kit",
    "USB Cable",
    "Figma License",
    "Wireless Mouse",
    "Monitor Stand",
    "Keyboard",
    "Webcam"
]


def load_labels(labels_dir):
    """Load all label files from the labels directory."""
    labels = []
    if os.path.exists(labels_dir):
        for filename in os.listdir(labels_dir):
            if filename.endswith('.json'):
                with open(os.path.join(labels_dir, filename)) as f:
                    labels.append(json.load(f))
    return labels


def simulate_prediction(scene_id, true_items):
    """
    Simulate ML prediction with confidence scores.

    In a real implementation, this would:
    1. Load and preprocess the image
    2. Extract features (resize, normalize, etc.)
    3. Run through trained model
    4. Return predicted labels with confidence

    For demonstration, we simulate predictions based on ground truth
    with some noise to show the threshold policy in action.
    """
    predictions = []

    # Predict items that are actually present (high confidence, some noise)
    for item in true_items:
        confidence = random.uniform(0.75, 0.99)
        predictions.append({
            "name": item,
            "confidence": round(confidence, 2)
        })

    # Sometimes predict items that aren't there (false positives with low confidence)
    if random.random() < 0.3:
        other_items = [i for i in KNOWN_ITEMS if i not in true_items]
        if other_items:
            false_positive = random.choice(other_items)
            predictions.append({
                "name": false_positive,
                "confidence": round(random.uniform(0.40, 0.70), 2)
            })

    return {
        "scene_id": scene_id,
        "predictions": predictions,
        "timestamp": datetime.now().isoformat()
    }


def run_classifier(labels_dir="ml/shelf_dataset/labels", output_dir="ml/predictions"):
    """
    Run the classifier on all scenes and generate prediction files.
    """
    os.makedirs(output_dir, exist_ok=True)

    labels = load_labels(labels_dir)
    all_predictions = []

    print("\n" + "="*60)
    print("SHELF IMAGE CLASSIFIER")
    print("="*60)

    for label in labels:
        scene_id = label["scene_id"]
        true_items = label["items_present"]

        # Run prediction
        prediction = simulate_prediction(scene_id, true_items)
        all_predictions.append(prediction)

        # Save individual prediction file
        output_path = os.path.join(output_dir, f"{scene_id}_prediction.json")
        with open(output_path, 'w') as f:
            json.dump(prediction, f, indent=2)

        print(f"\n📷 Scene: {scene_id}")
        print(f"   Ground truth: {true_items}")
        print(f"   Predictions:")
        for pred in prediction["predictions"]:
            conf_bar = "█" * int(pred["confidence"] * 10)
            print(f"      • {pred['name']}: {pred['confidence']:.2f} [{conf_bar}]")

    # Save combined predictions
    combined_path = os.path.join(output_dir, "all_predictions.json")
    with open(combined_path, 'w') as f:
        json.dump(all_predictions, f, indent=2)

    print(f"\n✅ Predictions saved to {output_dir}/")
    return all_predictions


if __name__ == "__main__":
    predictions = run_classifier()
