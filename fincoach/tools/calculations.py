from typing import Dict


def calculate_apr_cost(balance: float, apr: float, months: int = 12) -> Dict:
    """Calculate the cost of carrying a balance at a given APR.

    Args:
        balance: The principal amount owed.
        apr: Annual percentage rate (e.g. 24.99 for 24.99%).
        months: Number of months to project (default 12).

    Returns:
        Dict with monthly interest, yearly interest, and total cost.
    """
    monthly_rate = apr / 12 / 100
    total_interest = balance * monthly_rate * months
    return {
        "balance": balance,
        "apr": apr,
        "monthly_interest": balance * monthly_rate,
        "yearly_interest": total_interest,
        "total_cost": balance + total_interest,
    }


def categorize_transaction(transaction: Dict) -> str:
    """Assign a spending category based on the transaction description.

    Simple keyword matching — good enough for demo purposes.
    """
    description = transaction.get("description", "").lower()

    if any(word in description for word in ["restaurant", "cafe", "food", "doordash"]):
        return "dining"
    elif any(word in description for word in ["grocery", "market", "safeway"]):
        return "groceries"
    elif any(word in description for word in ["gas", "fuel", "shell", "chevron"]):
        return "transportation"
    elif any(word in description for word in ["netflix", "spotify", "subscription"]):
        return "subscriptions"
    else:
        return "other"
