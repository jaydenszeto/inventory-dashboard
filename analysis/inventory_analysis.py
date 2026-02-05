"""
Inventory Data Science Analysis
Module 4, Section 1: Understanding Your Data

This script transforms raw inventory data into actionable insights
using Pandas for analysis and Matplotlib for visualization.
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:3000/api/inventory"
LOW_STOCK_THRESHOLD = 10


def fetch_inventory():
    """Fetch inventory data from the API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching inventory: {e}")
        # Fallback to sample data for demonstration
        return [
            {"id": 1, "name": "Arduino Kit", "quantity": 5, "category": "Hardware", "status": "Available"},
            {"id": 2, "name": "Figma License", "quantity": 20, "category": "Software", "status": "Available"},
            {"id": 3, "name": "Wireless Mouse", "quantity": 25, "category": "Electronics", "status": "Available"},
            {"id": 4, "name": "USB Cable", "quantity": 3, "category": "Hardware", "status": "Available"},
            {"id": 5, "name": "Monitor Stand", "quantity": 8, "category": "Furniture", "status": "Unavailable"},
        ]


def analyze_inventory(data):
    """Transform inventory data into a Pandas DataFrame and compute insights."""
    df = pd.DataFrame(data)

    print("\n" + "="*60)
    print("INVENTORY DATA SCIENCE ANALYSIS")
    print("="*60)
    print(f"Analysis generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 1. Display the full inventory table
    print("\n📦 INVENTORY TABLE")
    print("-"*60)
    print(df.to_string(index=False))

    # 2. Total number of items
    total_products = len(df)
    total_units = df['quantity'].sum()

    print("\n📊 SUMMARY STATISTICS")
    print("-"*60)
    print(f"Total Products:     {total_products}")
    print(f"Total Units:        {total_units}")

    # 3. Group by category
    category_summary = df.groupby('category').agg({
        'name': 'count',
        'quantity': 'sum'
    }).rename(columns={'name': 'product_count', 'quantity': 'total_units'})

    print("\n📁 ITEMS BY CATEGORY")
    print("-"*60)
    print(category_summary.to_string())

    # 4. Low stock items
    low_stock = df[df['quantity'] < LOW_STOCK_THRESHOLD]
    low_stock_count = len(low_stock)

    print(f"\n⚠️  LOW STOCK ITEMS (quantity < {LOW_STOCK_THRESHOLD})")
    print("-"*60)
    if low_stock_count > 0:
        print(low_stock[['name', 'category', 'quantity']].to_string(index=False))
    else:
        print("No items are low stock.")
    print(f"\nTotal low stock items: {low_stock_count}")

    # 5. Status breakdown
    if 'status' in df.columns:
        status_summary = df.groupby('status').size()
        print("\n🔄 STATUS BREAKDOWN")
        print("-"*60)
        for status, count in status_summary.items():
            print(f"{status}: {count}")

    return df, category_summary, low_stock


def create_visualization(df, category_summary):
    """Generate visualizations for inventory data."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Inventory Dashboard - Data Science Analysis', fontsize=14, fontweight='bold')

    # Chart 1: Items by Category (Bar Chart)
    ax1 = axes[0]
    colors = ['#4a90d9', '#50c878', '#f39c12', '#e74c3c', '#9b59b6']
    category_summary['total_units'].plot(
        kind='bar',
        ax=ax1,
        color=colors[:len(category_summary)],
        edgecolor='black',
        linewidth=0.5
    )
    ax1.set_title('Total Units by Category', fontweight='bold')
    ax1.set_xlabel('Category')
    ax1.set_ylabel('Total Units')
    ax1.tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for i, v in enumerate(category_summary['total_units']):
        ax1.text(i, v + 0.5, str(v), ha='center', fontweight='bold')

    # Chart 2: Stock Level Distribution (Horizontal Bar)
    ax2 = axes[1]
    df_sorted = df.sort_values('quantity', ascending=True)
    bar_colors = ['#e74c3c' if q < LOW_STOCK_THRESHOLD else '#50c878' for q in df_sorted['quantity']]

    ax2.barh(df_sorted['name'], df_sorted['quantity'], color=bar_colors, edgecolor='black', linewidth=0.5)
    ax2.axvline(x=LOW_STOCK_THRESHOLD, color='orange', linestyle='--', linewidth=2, label=f'Low Stock Threshold ({LOW_STOCK_THRESHOLD})')
    ax2.set_title('Stock Levels by Item', fontweight='bold')
    ax2.set_xlabel('Quantity')
    ax2.legend()

    plt.tight_layout()

    # Save the figure
    output_path = 'analysis/inventory_chart.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n📈 Chart saved to: {output_path}")

    plt.show()


def export_summary(df, category_summary, low_stock):
    """Export summary data as JSON for dashboard consumption."""
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_products": len(df),
        "total_units": int(df['quantity'].sum()),
        "low_stock_count": len(low_stock),
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "by_category": category_summary.reset_index().to_dict(orient='records'),
        "low_stock_items": low_stock[['id', 'name', 'category', 'quantity']].to_dict(orient='records') if len(low_stock) > 0 else [],
        "status_breakdown": df.groupby('status').size().to_dict() if 'status' in df.columns else {}
    }

    output_path = 'analysis/inventory_summary.json'
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"📄 Summary JSON saved to: {output_path}")
    return summary


def main():
    # Fetch data
    inventory_data = fetch_inventory()

    # Analyze with Pandas
    df, category_summary, low_stock = analyze_inventory(inventory_data)

    # Create visualization
    create_visualization(df, category_summary)

    # Export for dashboard
    summary = export_summary(df, category_summary, low_stock)

    print("\n" + "="*60)
    print("✅ Analysis complete!")
    print("="*60)


if __name__ == "__main__":
    main()
