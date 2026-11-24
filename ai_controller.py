
import requests


class AIController:

    def __init__(self, model="qwen2.5-coder:1.5b"):

        self.model = model
        self.api_url = "http://localhost:11434/api/chat"

        self.conversation = [
            {
                "role": "system",
                "content": (
                    "You are an autonomous software "
                    "development assistant. "
                    "You help plan projects, write code, "
                    "debug errors and explain technical tasks. "
                    "Give clear, structured responses."
                )
            }
        ]

    def ask_ai(self, instruction):

        self.conversation.append({
            "role": "user",
            "content": instruction
        })

        payload = {
            "model": self.model,
            "messages": self.conversation,
            "stream": False
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=180
            )

            response.raise_for_status()

            result = response.json()

            ai_response = result["message"]["content"]

            self.conversation.append({
                "role": "assistant",
                "content": ai_response
            })

            return ai_response

        except requests.exceptions.RequestException as error:

            return f"Ollama connection error: {error}"

    def reset_conversation(self):

        self.conversation = self.conversation[:1]


if __name__ == "__main__":

    bot = AIController()

    print("=" * 50)
    print("AUTONOMOUS CODING BOT - AI CONTROLLER")
    print("=" * 50)

    while True:

        instruction = input("\nEnter your instruction: ")

        if instruction.lower() in ["exit", "quit"]:
            print("AI Controller stopped.")
            break

        if instruction.lower() == "reset":
            bot.reset_conversation()
            print("Conversation reset.")
            continue

        print("\nAI is thinking...\n")

        answer = bot.ask_ai(instruction)

        print("=" * 50)
        print("AI RESPONSE")
        print("=" * 50)

        print(answer)
