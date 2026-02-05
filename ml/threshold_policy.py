"""
Threshold Policy & Filtering
Module 4, Section 2: Machine Learning

This module implements the system policy that decides which
predictions are trusted enough to act on automatically.
"""

import json
import os
from datetime import datetime

# Confidence threshold - predictions below this require manual review
CONF_THRESHOLD = 0.90


def apply_threshold_policy(predictions):
    """
    Split predictions into accepted and uncertain based on confidence threshold.

    Returns:
        accepted: List of predictions with confidence >= CONF_THRESHOLD
        uncertain: List of predictions with confidence < CONF_THRESHOLD
        audit_events: List of audit events for uncertain predictions
    """
    accepted = []
    uncertain = []
    audit_events = []

    print("\n" + "="*60)
    print(f"THRESHOLD POLICY (threshold = {CONF_THRESHOLD})")
    print("="*60)

    for scene in predictions:
        scene_id = scene["scene_id"]
        scene_accepted = []
        scene_uncertain = []

        for pred in scene["predictions"]:
            if pred["confidence"] >= CONF_THRESHOLD:
                scene_accepted.append(pred)
            else:
                scene_uncertain.append(pred)
                # Generate audit event for uncertain prediction
                audit_events.append({
                    "timestamp": datetime.now().isoformat(),
                    "scene_id": scene_id,
                    "item": pred["name"],
                    "event_type": "UNCERTAIN",
                    "confidence": pred["confidence"],
                    "recommended_action": "MANUAL_REVIEW",
                    "reason": f"Confidence {pred['confidence']:.2f} below threshold {CONF_THRESHOLD}"
                })

        if scene_accepted:
            accepted.append({
                "scene_id": scene_id,
                "predictions": scene_accepted
            })

        if scene_uncertain:
            uncertain.append({
                "scene_id": scene_id,
                "predictions": scene_uncertain
            })

        # Print results
        print(f"\n📷 Scene: {scene_id}")
        print(f"   ✅ Accepted ({len(scene_accepted)}):")
        for pred in scene_accepted:
            print(f"      • {pred['name']}: {pred['confidence']:.2f}")
        print(f"   ⚠️  Uncertain ({len(scene_uncertain)}):")
        for pred in scene_uncertain:
            print(f"      • {pred['name']}: {pred['confidence']:.2f} → REQUIRES REVIEW")

    # Summary
    total_accepted = sum(len(s["predictions"]) for s in accepted)
    total_uncertain = sum(len(s["predictions"]) for s in uncertain)

    print("\n" + "-"*60)
    print("SUMMARY")
    print("-"*60)
    print(f"Total accepted predictions:  {total_accepted}")
    print(f"Total uncertain predictions: {total_uncertain}")
    print(f"Audit events generated:      {len(audit_events)}")

    return accepted, uncertain, audit_events


def save_filtered_results(accepted, uncertain, audit_events, output_dir="ml/predictions"):
    """Save filtered results to files."""
    os.makedirs(output_dir, exist_ok=True)

    # Save accepted predictions
    with open(os.path.join(output_dir, "accepted_predictions.json"), 'w') as f:
        json.dump(accepted, f, indent=2)

    # Save uncertain predictions
    with open(os.path.join(output_dir, "uncertain_predictions.json"), 'w') as f:
        json.dump(uncertain, f, indent=2)

    # Save audit events
    with open(os.path.join(output_dir, "uncertain_audit_events.json"), 'w') as f:
        json.dump(audit_events, f, indent=2)

    print(f"\n📁 Filtered results saved to {output_dir}/")


def run_threshold_policy(predictions_path="ml/predictions/all_predictions.json"):
    """Load predictions and apply threshold policy."""
    with open(predictions_path) as f:
        predictions = json.load(f)

    accepted, uncertain, audit_events = apply_threshold_policy(predictions)
    save_filtered_results(accepted, uncertain, audit_events)

    return accepted, uncertain, audit_events


if __name__ == "__main__":
    # First run classifier if predictions don't exist
    if not os.path.exists("ml/predictions/all_predictions.json"):
        from classifier import run_classifier
        run_classifier()

    run_threshold_policy()
