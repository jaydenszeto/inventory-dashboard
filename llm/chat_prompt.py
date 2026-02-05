"""
LLM Chat Interface for Inventory
Module 4, Section 3: LLMs as Interfaces

This module provides a natural language interface for querying inventory.
LLMs act as a reasoning layer on top of structured data, not as a replacement.
"""

import json
import requests

API_URL = "http://localhost:3000/api/inventory"

# System prompt that defines LLM behavior and guardrails
SYSTEM_PROMPT = """You are an Inventory Assistant for Open Project. Your role is to help users understand and query the inventory system using natural language.

## CAPABILITIES (what you CAN do):
- Answer questions about current inventory levels
- Identify low stock items (quantity < 10)
- Summarize inventory by category
- Explain what items are available or unavailable
- Provide counts and totals

## LIMITATIONS (what you CANNOT do):
- You CANNOT modify, add, or delete inventory items
- You CANNOT make purchases or orders
- You CANNOT access external systems or databases beyond what's provided
- You CANNOT guarantee real-time accuracy (data may be slightly stale)

## GUARDRAILS:
- If asked to modify inventory, politely explain you're read-only and direct users to the dashboard
- If asked about items not in the provided data, say "I don't have information about that item"
- Always cite the data provided to you, don't make up information
- Be concise and helpful

## CURRENT INVENTORY DATA:
{inventory_data}

## INSTRUCTIONS:
Answer the user's question based ONLY on the inventory data provided above. Be helpful, accurate, and concise.
"""


def fetch_inventory():
    """Fetch current inventory from API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return [
            {"id": 1, "name": "Arduino Kit", "quantity": 5, "category": "Hardware", "status": "Available"},
            {"id": 2, "name": "Figma License", "quantity": 20, "category": "Software", "status": "Available"},
            {"id": 3, "name": "Wireless Mouse", "quantity": 25, "category": "Electronics", "status": "Available"},
        ]


def build_prompt(user_query):
    """Build the full prompt with inventory context."""
    inventory = fetch_inventory()
    inventory_json = json.dumps(inventory, indent=2)

    system = SYSTEM_PROMPT.format(inventory_data=inventory_json)

    return {
        "system": system,
        "user": user_query,
        "inventory": inventory
    }


def format_inventory_for_context(inventory):
    """Format inventory as a readable summary for the LLM."""
    lines = ["Current Inventory:"]
    lines.append("-" * 40)

    for item in inventory:
        status_icon = "✅" if item.get("status") == "Available" else "❌"
        low_stock = " ⚠️ LOW" if item["quantity"] < 10 else ""
        lines.append(f"{status_icon} {item['name']}")
        lines.append(f"   Category: {item['category']}")
        lines.append(f"   Quantity: {item['quantity']}{low_stock}")
        lines.append("")

    return "\n".join(lines)


# Example queries for testing
EXAMPLE_QUERIES = [
    "Which hardware items are low stock?",
    "How many categories exist in inventory?",
    "What items are currently available?",
    "How many total units do we have?",
    "List all software items",
]


def demo_chat_interface():
    """Demo the chat interface design."""
    print("\n" + "="*60)
    print("LLM INVENTORY CHAT - Interface Demo")
    print("="*60)

    inventory = fetch_inventory()

    print("\n📦 INVENTORY CONTEXT (provided to LLM):")
    print("-"*60)
    print(format_inventory_for_context(inventory))

    print("\n💬 EXAMPLE QUERIES:")
    print("-"*60)
    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        print(f"   {i}. \"{query}\"")

    print("\n🛡️ GUARDRAILS:")
    print("-"*60)
    print("   • Read-only access (no modifications)")
    print("   • Context-limited (only sees provided inventory)")
    print("   • Honest about limitations")

    # Build a sample prompt
    sample_prompt = build_prompt("Which hardware items are low stock?")

    print("\n📝 SAMPLE PROMPT STRUCTURE:")
    print("-"*60)
    print(f"System prompt length: {len(sample_prompt['system'])} chars")
    print(f"User query: \"{sample_prompt['user']}\"")
    print(f"Inventory items in context: {len(sample_prompt['inventory'])}")

    # Save the prompt template
    with open("llm/prompt_template.json", 'w') as f:
        json.dump({
            "system_prompt": SYSTEM_PROMPT,
            "example_queries": EXAMPLE_QUERIES,
            "guardrails": [
                "Read-only access - cannot modify inventory",
                "Context-limited - only sees provided data",
                "Honest about uncertainty",
                "Directs users to dashboard for modifications"
            ]
        }, f, indent=2)

    print("\n✅ Prompt template saved to llm/prompt_template.json")


if __name__ == "__main__":
    demo_chat_interface()
