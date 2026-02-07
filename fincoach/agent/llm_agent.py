import os
import json
from anthropic import Anthropic
from typing import Dict, List, Any
from tools.financial_tools import TOOLS, TOOL_FUNCTIONS

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class FinancialAgent:
    """LLM agent that uses Claude with tool calling to answer financial questions.

    The agent loop:
    1. Send user message + tool definitions to Claude.
    2. If Claude responds with a tool_use block, execute the tool locally.
    3. Feed the tool result back to Claude.
    4. Repeat until Claude produces a final text response.

    This lets Claude decide *when* to call tools (e.g. check balance)
    and *how* to interpret the results for the user.
    """

    def __init__(self, account_id: str):
        self.account_id = account_id
        self.conversation_history: List[Dict[str, Any]] = []

    def chat(self, user_message: str) -> str:
        """Process a user message and return the agent's text response.

        May invoke one or more tools before producing the final answer.
        """
        system_prompt = f"""You are FinCoach, a financial literacy teacher.

Your job: Teach financial concepts using the user's REAL transaction data.

Rules:
1. ALWAYS use tools to get real data - NEVER make up numbers
2. Explain concepts simply, like teaching a friend
3. When you use a tool, explain what the numbers mean
4. If a tool returns "verified": True, you can trust that data
5. Never hallucinate financial facts - if you don't know, say so
6. Keep responses concise for voice (2-3 sentences max)

The user's account ID is: {self.account_id}"""

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=self.conversation_history,
            tools=TOOLS,
        )

        # Tool-use loop: keep calling tools until Claude gives a final text answer.
        while response.stop_reason == "tool_use":
            tool_use_block = next(
                block for block in response.content if block.type == "tool_use"
            )
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input

            # Inject account_id if the tool needs it but Claude didn't provide it
            if "account_id" not in tool_input:
                tool_input["account_id"] = self.account_id

            # Execute the tool locally
            tool_result = TOOL_FUNCTIONS[tool_name](**tool_input)

            # Append the assistant's tool-use turn
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content,
            })

            # Append the tool result so Claude can interpret it
            self.conversation_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": json.dumps(tool_result),
                    }
                ],
            })

            # Ask Claude to continue with the tool result
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=self.conversation_history,
                tools=TOOLS,
            )

        # Extract the final text from the response
        final_text = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )

        self.conversation_history.append({
            "role": "assistant",
            "content": final_text,
        })

        return final_text
