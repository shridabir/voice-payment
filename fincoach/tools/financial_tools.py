from typing import Dict, Any
from .nessie_client import NessieClient
from .calculations import calculate_apr_cost, categorize_transaction

nessie = NessieClient()


def get_balance_tool(account_id: str) -> Dict[str, Any]:
    """Fetch account balance from Nessie and return verified result."""
    balance = nessie.get_balance(account_id)
    return {
        "balance": balance,
        "source": "nessie_api",
        "verified": True,
    }


def get_spending_by_category_tool(account_id: str, days: int = 30) -> Dict[str, Any]:
    """Pull transactions from Nessie and group spending by category."""
    transactions = nessie.get_transactions(account_id, days)

    categories = {}
    total = 0

    for txn in transactions:
        category = categorize_transaction(txn)
        amount = txn.get("amount", 0)
        categories[category] = categories.get(category, 0) + amount
        total += amount

    return {
        "categories": categories,
        "total": total,
        "period_days": days,
        "verified": True,
        "source": "nessie_api",
    }


def check_affordability_tool(account_id: str, amount: float) -> Dict[str, Any]:
    """Check whether a purchase is safe given the current balance.

    Maintains a $50 buffer — if the purchase would leave less than $50,
    it's flagged as unaffordable.
    """
    balance = nessie.get_balance(account_id)
    buffer = 50
    can_afford = (balance - amount) >= buffer

    return {
        "can_afford": can_afford,
        "current_balance": balance,
        "purchase_amount": amount,
        "balance_after": balance - amount,
        "buffer_maintained": (balance - amount) >= buffer,
        "recommendation": "Safe to purchase" if can_afford else f"Wait - would leave only ${balance - amount:.2f}",
        "verified": True,
    }


# Tool definitions for Claude's tool_use API.
# Each entry describes a callable tool with its name, description, and input schema.
TOOLS = [
    {
        "name": "get_balance",
        "description": "Get the current account balance. Use this when user asks about their balance or available money.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "User's account ID"}
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "get_spending_by_category",
        "description": "Analyze spending by category (dining, groceries, etc). Use when user asks where their money goes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "days": {"type": "integer", "description": "Number of days to analyze (default 30)"},
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "check_affordability",
        "description": "Check if user can afford a purchase. Use when user asks 'can I afford X?'",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "amount": {"type": "number", "description": "Purchase amount in dollars"},
            },
            "required": ["account_id", "amount"],
        },
    },
]

# Maps tool names to their Python implementations for the agent loop.
TOOL_FUNCTIONS = {
    "get_balance": get_balance_tool,
    "get_spending_by_category": get_spending_by_category_tool,
    "check_affordability": check_affordability_tool,
}
