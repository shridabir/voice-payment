import asyncio
from agent.llm_agent import FinancialAgent
from agent.voice_handler import VoiceHandler
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    account_id = os.getenv("DEMO_ACCOUNT_ID", "your_nessie_account_id")
    agent = FinancialAgent(account_id)
    voice = VoiceHandler()

    print("🎯 FinCoach Voice Assistant Ready!")
    print("Press Ctrl+C to exit\n")

    while True:
        try:
            user_input = voice.listen(duration=5)
            print(f"You: {user_input}")

            if not user_input.strip():
                continue

            response = agent.chat(user_input)
            print(f"FinCoach: {response}\n")

            await voice.speak(response)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
