import requests
from typing import Dict, List
import os


class NessieClient:
    """Client for the Capital One Nessie sandbox banking API.

    Provides access to accounts, balances, and transaction history.
    All endpoints require an API key from http://api.nessieisreal.com/.
    """

    def __init__(self):
        self.base_url = "http://api.nessieisreal.com"
        self.api_key = os.getenv("NESSIE_API_KEY")

    def get_accounts(self, customer_id: str) -> List[Dict]:
        """Fetch all accounts for a customer."""
        url = f"{self.base_url}/customers/{customer_id}/accounts?key={self.api_key}"
        response = requests.get(url)
        return response.json()

    def get_balance(self, account_id: str) -> float:
        """Fetch current balance for a single account."""
        url = f"{self.base_url}/accounts/{account_id}?key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return data.get("balance", 0)

    def get_transactions(self, account_id: str, days: int = 30) -> List[Dict]:
        """Fetch recent purchases for an account (capped at 20)."""
        url = f"{self.base_url}/accounts/{account_id}/purchases?key={self.api_key}"
        response = requests.get(url)
        transactions = response.json()
        return transactions[:20]
