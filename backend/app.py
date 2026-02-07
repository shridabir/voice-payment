from flask import Flask, request, jsonify
from flask_cors import CORS
from nessie_client import NessieClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

nessie = NessieClient(os.getenv("NESSIE_API_KEY"))

# Replace these with real IDs from your Nessie dashboard after signing up
DEMO_CUSTOMER_ID = "YOUR_CUSTOMER_ID"
DEMO_ACCOUNT_ID = "YOUR_ACCOUNT_ID"

# Known contacts mapped to their Nessie account IDs
CONTACTS = {
    "mike": {"name": "Mike Chen", "account_id": "RECIPIENT_ACCOUNT_1"},
    "sarah": {"name": "Sarah Johnson", "account_id": "RECIPIENT_ACCOUNT_2"},
    "alex": {"name": "Alex Kim", "account_id": "RECIPIENT_ACCOUNT_3"},
}

# In-memory conversation state keyed by session ID.
# Tracks multi-turn flows like payment confirmations.
conversation_state = {}


@app.route("/api/chat", methods=["POST"])
def chat():
    """Main conversational endpoint.

    Accepts { message, session_id } and returns { response }.
    Handles greetings, help, payment intents, and confirmation flows.
    """
    user_message = request.json.get("message", "")
    session_id = request.json.get("session_id", "default")

    if session_id not in conversation_state:
        conversation_state[session_id] = {"step": "idle"}

    state = conversation_state[session_id]
    lower_msg = user_message.lower()

    # --- Greeting ---
    if any(word in lower_msg for word in ["hello", "hi", "hey"]):
        return jsonify(
            {"response": "Hi! I'm your payment assistant. Try saying 'Send Mike 20 dollars'"}
        )

    # --- Help ---
    if "help" in lower_msg:
        return jsonify(
            {"response": "Tell me who to pay and how much. Example: 'Send Sarah 15 dollars'"}
        )

    # --- Payment intent ---
    if any(word in lower_msg for word in ["send", "pay", "transfer"]):
        # Extract dollar amount (e.g. "20", "$20")
        amount_match = re.search(r"\$?(\d+)", user_message)
        amount = int(amount_match.group(1)) if amount_match else None

        # Match recipient name against known contacts
        recipient = None
        for name, contact in CONTACTS.items():
            if name in lower_msg:
                recipient = contact
                break

        if amount and recipient:
            state["pending_payment"] = {
                "recipient": recipient,
                "amount": amount,
                "description": "payment",
            }
            state["step"] = "awaiting_confirmation"
            return jsonify(
                {
                    "response": f"Sending ${amount} to {recipient['name']}. Say confirm to complete."
                }
            )
        else:
            return jsonify({"response": "Try saying 'Send Mike 20 dollars'"})

    # --- Confirmation / cancellation ---
    if state.get("step") == "awaiting_confirmation":
        if "confirm" in lower_msg or "yes" in lower_msg:
            payment = state["pending_payment"]
            try:
                nessie.create_transfer(
                    DEMO_ACCOUNT_ID,
                    payment["recipient"]["account_id"],
                    payment["amount"],
                    payment["description"],
                )
                conversation_state[session_id] = {"step": "idle"}
                return jsonify(
                    {
                        "response": f"Done! ${payment['amount']} sent to {payment['recipient']['name']}."
                    }
                )
            except Exception as e:
                return jsonify({"response": f"Payment failed: {str(e)}"})

        elif "cancel" in lower_msg or "no" in lower_msg:
            conversation_state[session_id] = {"step": "idle"}
            return jsonify({"response": "Payment cancelled."})

    # --- Fallback ---
    return jsonify({"response": "Try saying 'Send money to Mike' or ask for help."})


@app.route("/api/accounts", methods=["GET"])
def get_accounts():
    """Return all accounts for the demo customer (useful for testing)."""
    try:
        accounts = nessie.get_customer_accounts(DEMO_CUSTOMER_ID)
        return jsonify(accounts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
