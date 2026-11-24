
import json
import time
import requests
import pyautogui

from automation_engine import AutomationEngine


class ActionController:

    def __init__(self):

        self.model = "qwen2.5-coder:1.5b"
        self.api_url = "http://localhost:11434/api/chat"

        self.engine = AutomationEngine()

        self.screen_width, self.screen_height = pyautogui.size()

        self.allowed_actions = {
            "move_mouse",
            "click",
            "press_key",
            "hotkey",
            "paste_text",
            "scroll",
            "wait"
        }

        self.allowed_keys = {
            "enter", "tab", "space", "esc",
            "backspace", "delete",
            "up", "down", "left", "right",
            "home", "end", "pageup", "pagedown",
            "ctrl", "shift", "alt", "win",
            "r",
            "f1", "f2", "f3", "f4",
            "f5", "f6", "f7", "f8",
            "f9", "f10", "f11", "f12"
        }

        self.allowed_keys.update("abcdefghijklmnopqrstuvwxyz")
        self.allowed_keys.update("0123456789")

    # ==========================================
    # GENERATE AI ACTIONS
    # ==========================================

    def generate_actions(self, instruction):

        system_prompt = """
You are a desktop automation planner.

Convert the user's instruction into a JSON action plan.

Return ONLY valid JSON in this structure:

{
    "actions": [
        {"action": "hotkey", "keys": ["win", "r"]},
        {"action": "wait", "seconds": 1},
        {"action": "paste_text", "text": "notepad"},
        {"action": "press_key", "key": "enter"},
        {"action": "wait", "seconds": 2},
        {"action": "paste_text", "text": "Hello world"}
    ]
}

AVAILABLE ACTIONS:

1. move_mouse:
{"action":"move_mouse","x":500,"y":300}

2. click:
{"action":"click","x":500,"y":300}

3. press_key:
{"action":"press_key","key":"enter"}

4. hotkey:
{"action":"hotkey","keys":["ctrl","s"]}

5. paste_text:
{"action":"paste_text","text":"Your text here"}

6. scroll:
{"action":"scroll","amount":-3}

7. wait:
{"action":"wait","seconds":2}

RULES:
- Return JSON only.
- Never return Python code.
- Use only the available actions.
- Maximum 10 actions per plan.
- Use paste_text for text and code.
- Include waits when applications need time to open.
- Do not delete files.
- Do not execute destructive operations.
- Do not issue terminal commands.
- Never use open_program.
- Never invent action names.
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": instruction
                }
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 700
            }
        }

        response = requests.post(
            self.api_url,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        content = result.get(
            "message", {}
        ).get("content", "")

        if not content or not content.strip():
            raise ValueError("Ollama returned an empty response.")

        try:
            parsed = json.loads(content)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"AI returned invalid JSON: {content}"
            ) from error

        if not isinstance(parsed, dict):
            raise ValueError("AI response must be a JSON object.")

        actions = parsed.get("actions")

        if not isinstance(actions, list) or not actions:
            raise ValueError(
                "AI did not return a valid action list."
            )

        if len(actions) > 10:
            raise ValueError(
                "AI generated more than 10 actions."
            )

        # Validate every action before returning the plan.
        for action in actions:
            self.validate_action(action)

        return actions

    # ==========================================
    # VALIDATE ACTIONS
    # ==========================================

    def validate_action(self, action):

        if not isinstance(action, dict):
            raise ValueError("Invalid action format.")

        action_type = action.get("action")

        if action_type not in self.allowed_actions:
            raise ValueError(
                f"Unsupported action: {action_type}"
            )

        if action_type == "move_mouse":

            x = action.get("x")
            y = action.get("y")

            if type(x) is not int or type(y) is not int:
                raise ValueError(
                    "Mouse coordinates must be integers."
                )

            if not (
                0 <= x < self.screen_width
                and 0 <= y < self.screen_height
            ):
                raise ValueError(
                    "Mouse coordinates outside screen."
                )

        elif action_type == "click":

            x = action.get("x")
            y = action.get("y")

            if type(x) is not int or type(y) is not int:
                raise ValueError(
                    "Click coordinates must be integers."
                )

            if not (
                0 <= x < self.screen_width
                and 0 <= y < self.screen_height
            ):
                raise ValueError(
                    "Click coordinates outside screen."
                )

        elif action_type == "press_key":

            if action.get("key") not in self.allowed_keys:
                raise ValueError("Keyboard key not allowed.")

        elif action_type == "hotkey":

            keys = action.get("keys")

            if not isinstance(keys, list) or not 1 <= len(keys) <= 4:
                raise ValueError("Invalid hotkey combination.")

            if any(key not in self.allowed_keys for key in keys):
                raise ValueError(
                    "Hotkey contains an unsupported key."
                )

        elif action_type == "paste_text":

            text = action.get("text")

            if not isinstance(text, str) or len(text) > 2000:
                raise ValueError(
                    "Invalid or excessively long text."
                )

        elif action_type == "scroll":

            amount = action.get("amount")

            if type(amount) is not int or not -10 <= amount <= 10:
                raise ValueError("Invalid scroll amount.")

        elif action_type == "wait":

            seconds = action.get("seconds")

            if (
                type(seconds) not in (int, float)
                or not 0 <= seconds <= 10
            ):
                raise ValueError("Invalid wait duration.")

    # ==========================================
    # EXECUTE ONE ACTION
    # ==========================================

    def execute_action(self, action):

        self.validate_action(action)

        action_type = action["action"]

        if action_type == "move_mouse":

            self.engine.move_mouse(
                action["x"],
                action["y"]
            )

        elif action_type == "click":

            self.engine.click(
                action["x"],
                action["y"]
            )

        elif action_type == "press_key":

            self.engine.press_key(
                action["key"]
            )

        elif action_type == "hotkey":

            self.engine.hotkey(
                *action["keys"]
            )

        elif action_type == "paste_text":

            self.engine.paste_text(
                action["text"]
            )

        elif action_type == "scroll":

            self.engine.scroll(
                action["amount"]
            )

        elif action_type == "wait":

            time.sleep(action["seconds"])

    # ==========================================
    # EXECUTE COMPLETE PLAN
    # ==========================================

    def execute_plan(self, plan):

        # Support both a list and the older dictionary format.
        if isinstance(plan, dict):
            actions = plan.get("actions")
        else:
            actions = plan

        if not isinstance(actions, list) or not 1 <= len(actions) <= 10:
            raise ValueError("Invalid action plan.")

        # Validate everything before executing.
        for action in actions:
            self.validate_action(action)

        print("\nAI GENERATED ACTION PLAN")

        for number, action in enumerate(actions, 1):
            print(f"{number}. {action}")

        approval = input(
            "\nExecute these actions? (y/n): "
        ).strip().lower()

        if approval != "y":
            print("Execution cancelled.")
            return

        self.engine.start()

        try:

            for number, action in enumerate(actions, 1):

                print(
                    f"Executing action {number}: "
                    f"{action['action']}"
                )

                self.execute_action(action)

        finally:
            self.engine.stop()

        print("\nAction plan completed.")

    # ==========================================
    # COMMAND LINE MODE
    # ==========================================

    def run(self):

        print("=" * 50)
        print("AUTONOMOUS CODING BOT - ACTION CONTROLLER")
        print("=" * 50)

        while True:

            instruction = input(
                "\nWhat should the bot do? "
            ).strip()

            if instruction.lower() in ["exit", "quit"]:
                print("Action controller stopped.")
                break

            if not instruction:
                continue

            try:

                print("\nAI is planning actions...")

                actions = self.generate_actions(instruction)

                self.execute_plan(actions)

            except Exception as error:

                print("\nERROR:", error)


if __name__ == "__main__":

    bot = ActionController()
    bot.run()
