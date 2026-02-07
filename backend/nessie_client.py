import requests


class NessieClient:
    """Client for the Capital One Nessie API (http://api.nessieisreal.com).

    Nessie is a sandbox banking API that simulates accounts, customers,
    and transfers. All requests require an API key passed as a query param.
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.nessieisreal.com"

    def get_customer_accounts(self, customer_id):
        """Fetch all accounts belonging to a customer."""
        url = f"{self.base_url}/customers/{customer_id}/accounts"
        response = requests.get(url, params={"key": self.api_key})
        return response.json()

    def get_account(self, account_id):
        """Fetch a single account by ID."""
        url = f"{self.base_url}/accounts/{account_id}"
        response = requests.get(url, params={"key": self.api_key})
        return response.json()

    def create_transfer(self, account_id, payee_id, amount, description):
        """Create a transfer from one account to another.

        Uses 'balance' as the medium (direct account balance transfer).
        """
        url = f"{self.base_url}/accounts/{account_id}/transfers"
        payload = {
            "medium": "balance",
            "payee_id": payee_id,
            "amount": amount,
            "transaction_date": "2024-01-15",
            "description": description,
        }
        response = requests.post(url, json=payload, params={"key": self.api_key})
        return response.json()
