
import pyautogui
import pyperclip
import time


class AutomationEngine:

    def __init__(self):
        self.running = False

        # Emergency stop: move mouse to top-left corner
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3

    def start(self):
        self.running = True
        print("Automation engine started.")

    def stop(self):
        self.running = False
        print("Automation engine stopped.")

    def move_mouse(self, x, y, duration=0.5):
        if self.running:
            pyautogui.moveTo(x, y, duration=duration)

    def click(self, x=None, y=None):
        if self.running:
            pyautogui.click(x, y)

    def press_key(self, key):
        if self.running:
            pyautogui.press(key)

    def hotkey(self, *keys):
        if self.running:
            pyautogui.hotkey(*keys)

    def type_text(self, text, interval=0.02):
        if self.running:
            pyautogui.write(text, interval=interval)

    def paste_text(self, text):
        if self.running:
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")

    def screenshot(self):
        if self.running:
            return pyautogui.screenshot()

    def scroll(self, amount):
        if self.running:
            pyautogui.scroll(amount)


if __name__ == "__main__":

    bot = AutomationEngine()

    print("AUTONOMOUS CODING BOT")
    print("Starting in 5 seconds...")

    time.sleep(5)

    bot.start()

    # Move actual Windows mouse pointer
    width, height = pyautogui.size()
    bot.move_mouse(width // 2, height // 2)

    # Open Notepad
    bot.hotkey("win", "r")
    time.sleep(1)

    bot.type_text("notepad")
    bot.press_key("enter")

    time.sleep(2)

    # Type test message
    bot.type_text(
        "Hello! My autonomous coding bot is working."
    )

    bot.stop()

    print("Automation test completed.")
