"""
Reconciliation & Audit Logging
Module 4, Section 2: Machine Learning

This module compares ML predictions against the inventory database
to identify discrepancies and generate appropriate audit logs.
"""

import json
import os
import requests
from datetime import datetime

# API endpoint for inventory
API_URL = "http://localhost:3000/api/inventory"
AUDIT_LOG_PATH = "ml/audit_log.jsonl"


def fetch_inventory():
    """Fetch current inventory from the database."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Warning: Could not fetch from API ({e}), using fallback data")
        return [
            {"id": 1, "name": "Arduino Kit", "quantity": 5, "category": "Hardware", "status": "Available"},
            {"id": 2, "name": "Figma License", "quantity": 20, "category": "Software", "status": "Available"},
            {"id": 3, "name": "Wireless Mouse", "quantity": 25, "category": "Electronics", "status": "Available"},
        ]


def reconcile(accepted_predictions, uncertain_predictions, inventory):
    """
    Compare predictions against inventory database.

    Reconciliation cases:
    - VERIFIED: DB says item exists (qty > 0) AND image predicts presence (high confidence)
    - DISCREPANCY: DB says out of stock (qty == 0) BUT image predicts presence
    - UNCERTAIN: Confidence below threshold → requires manual review
    - MISSING_FROM_DB: Predicted item not found in inventory system
    """

    # Build lookup from inventory
    inventory_lookup = {item["name"]: item for item in inventory}

    results = {
        "verified": [],
        "discrepancies": [],
        "uncertain": [],
        "missing_from_db": []
    }
    audit_events = []

    print("\n" + "="*60)
    print("RECONCILIATION: Observed vs Declared Inventory")
    print("="*60)

    # Process accepted predictions (high confidence)
    for scene in accepted_predictions:
        scene_id = scene["scene_id"]

        for pred in scene["predictions"]:
            item_name = pred["name"]
            confidence = pred["confidence"]

            if item_name not in inventory_lookup:
                # Item detected but not in our database
                results["missing_from_db"].append({
                    "scene_id": scene_id,
                    "item": item_name,
                    "confidence": confidence
                })
                audit_events.append({
                    "timestamp": datetime.now().isoformat(),
                    "scene_id": scene_id,
                    "item": item_name,
                    "event_type": "MISSING_FROM_DB",
                    "confidence": confidence,
                    "recommended_action": "ADD_TO_INVENTORY",
                    "db_quantity": None,
                    "observed": True
                })
            else:
                db_item = inventory_lookup[item_name]
                db_qty = db_item["quantity"]

                if db_qty > 0:
                    # VERIFIED: DB and observation agree
                    results["verified"].append({
                        "scene_id": scene_id,
                        "item": item_name,
                        "confidence": confidence,
                        "db_quantity": db_qty
                    })
                    audit_events.append({
                        "timestamp": datetime.now().isoformat(),
                        "scene_id": scene_id,
                        "item": item_name,
                        "event_type": "VERIFIED",
                        "confidence": confidence,
                        "recommended_action": "NONE",
                        "db_quantity": db_qty,
                        "observed": True
                    })
                else:
                    # DISCREPANCY: DB says 0 but we see it on shelf
                    results["discrepancies"].append({
                        "scene_id": scene_id,
                        "item": item_name,
                        "confidence": confidence,
                        "db_quantity": db_qty,
                        "issue": "DB shows 0 quantity but item observed on shelf"
                    })
                    audit_events.append({
                        "timestamp": datetime.now().isoformat(),
                        "scene_id": scene_id,
                        "item": item_name,
                        "event_type": "DISCREPANCY",
                        "confidence": confidence,
                        "recommended_action": "INVESTIGATE",
                        "db_quantity": db_qty,
                        "observed": True,
                        "issue": "Quantity mismatch - item observed but DB shows 0"
                    })

    # Process uncertain predictions
    for scene in uncertain_predictions:
        scene_id = scene["scene_id"]

        for pred in scene["predictions"]:
            results["uncertain"].append({
                "scene_id": scene_id,
                "item": pred["name"],
                "confidence": pred["confidence"]
            })
            audit_events.append({
                "timestamp": datetime.now().isoformat(),
                "scene_id": scene_id,
                "item": pred["name"],
                "event_type": "UNCERTAIN",
                "confidence": pred["confidence"],
                "recommended_action": "MANUAL_REVIEW",
                "db_quantity": inventory_lookup.get(pred["name"], {}).get("quantity"),
                "observed": "uncertain"
            })

    # Print results
    print(f"\n✅ VERIFIED ({len(results['verified'])} items)")
    for r in results["verified"]:
        print(f"   • {r['item']} (scene: {r['scene_id']}, conf: {r['confidence']:.2f}, db_qty: {r['db_quantity']})")

    print(f"\n🔴 DISCREPANCIES ({len(results['discrepancies'])} items)")
    for r in results["discrepancies"]:
        print(f"   • {r['item']} (scene: {r['scene_id']}, conf: {r['confidence']:.2f})")
        print(f"     Issue: {r['issue']}")

    print(f"\n⚠️  UNCERTAIN ({len(results['uncertain'])} items)")
    for r in results["uncertain"]:
        print(f"   • {r['item']} (scene: {r['scene_id']}, conf: {r['confidence']:.2f}) → MANUAL REVIEW")

    print(f"\n❓ MISSING FROM DB ({len(results['missing_from_db'])} items)")
    for r in results["missing_from_db"]:
        print(f"   • {r['item']} (scene: {r['scene_id']}, conf: {r['confidence']:.2f}) → ADD TO INVENTORY?")

    return results, audit_events


def write_audit_log(audit_events, log_path=AUDIT_LOG_PATH):
    """Write audit events to JSONL file."""
    os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else ".", exist_ok=True)

    with open(log_path, 'a') as f:
        for event in audit_events:
            f.write(json.dumps(event) + "\n")

    print(f"\n📝 {len(audit_events)} audit events written to {log_path}")


def save_reconciliation_results(results, output_path="ml/reconciliation_results.json"):
    """Save reconciliation results as JSON."""
    output = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "verified_count": len(results["verified"]),
            "discrepancy_count": len(results["discrepancies"]),
            "uncertain_count": len(results["uncertain"]),
            "missing_from_db_count": len(results["missing_from_db"])
        },
        "details": results
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"📁 Reconciliation results saved to {output_path}")


def run_reconciliation():
    """Main reconciliation pipeline."""
    # Load predictions
    try:
        with open("ml/predictions/accepted_predictions.json") as f:
            accepted = json.load(f)
        with open("ml/predictions/uncertain_predictions.json") as f:
            uncertain = json.load(f)
    except FileNotFoundError:
        print("Predictions not found. Running classifier and threshold policy first...")
        from classifier import run_classifier
        from threshold_policy import run_threshold_policy
        run_classifier()
        accepted, uncertain, _ = run_threshold_policy()

    # Fetch inventory
    inventory = fetch_inventory()

    # Run reconciliation
    results, audit_events = reconcile(accepted, uncertain, inventory)

    # Write outputs
    write_audit_log(audit_events)
    save_reconciliation_results(results)

    print("\n" + "="*60)
    print("✅ Reconciliation complete!")
    print("="*60)

    return results, audit_events


if __name__ == "__main__":
    run_reconciliation()
