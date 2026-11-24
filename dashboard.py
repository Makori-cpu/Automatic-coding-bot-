
import customtkinter as ctk
import threading
import queue

from action_controller import ActionController


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AutonomousCodingBotDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Autonomous Coding Bot")
        self.geometry("1150x760")
        self.minsize(950, 650)

        self.events = queue.Queue()
        self.action_controller = ActionController()

        self.pending_actions = []
        self.bot_running = False
        self.stop_requested = False
        self.plan_ready = False

        self.create_dashboard()
        self.after(200, self.process_events)

    def create_dashboard(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="AUTONOMOUS BOT",
            font=("Arial", 21, "bold")
        ).pack(pady=(35, 8))

        ctk.CTkLabel(
            self.sidebar,
            text="AI Coding Assistant",
            text_color="gray"
        ).pack(pady=(0, 35))

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="● READY",
            text_color="#22c55e",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=15)

        self.stop_button = ctk.CTkButton(
            self.sidebar,
            text="STOP AUTOMATION",
            command=self.stop_bot,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            height=42
        )
        self.stop_button.pack(
            padx=20, pady=15, fill="x"
        )

        ctk.CTkLabel(
            self.sidebar,
            text="LOCAL AI ENGINE",
            font=("Arial", 12, "bold")
        ).pack(pady=(45, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="Qwen2.5-Coder 1.5B",
            text_color="#60a5fa"
        ).pack()

        # MAIN AREA
        self.main = ctk.CTkFrame(
            self, corner_radius=0
        )
        self.main.grid(
            row=0, column=1,
            sticky="nsew", padx=15, pady=15
        )

        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self.main,
            text="Your AI Automation Workspace",
            font=("Arial", 26, "bold")
        ).grid(
            row=0, column=0,
            sticky="w", padx=25, pady=(25, 5)
        )

        ctk.CTkLabel(
            self.main,
            text="Give your AI instructions and watch it work.",
            text_color="gray"
        ).grid(
            row=1, column=0,
            sticky="w", padx=25
        )

        # INSTRUCTION AREA
        instruction_frame = ctk.CTkFrame(self.main)
        instruction_frame.grid(
            row=2, column=0,
            sticky="ew", padx=25, pady=20
        )
        instruction_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            instruction_frame,
            text="WHAT SHOULD YOUR BOT DO?",
            font=("Arial", 13, "bold")
        ).grid(
            row=0, column=0,
            sticky="w", padx=15, pady=10
        )

        self.instruction_input = ctk.CTkTextbox(
            instruction_frame, height=100
        )
        self.instruction_input.grid(
            row=1, column=0,
            sticky="ew", padx=15, pady=5
        )

        self.generate_button = ctk.CTkButton(
            instruction_frame,
            text="GENERATE ACTION PLAN",
            command=self.generate_plan,
            height=40
        )
        self.generate_button.grid(
            row=2, column=0,
            sticky="w", padx=15, pady=15
        )

        # APPROVAL BUTTONS
        self.approve_button = ctk.CTkButton(
            instruction_frame,
            text="APPROVE & EXECUTE",
            command=self.approve_plan,
            fg_color="#15803d",
            hover_color="#166534",
            height=40,
            state="disabled"
        )
        self.approve_button.grid(
            row=2, column=0,
            sticky="e", padx=15, pady=15
        )

        # OUTPUT AREA
        output_frame = ctk.CTkFrame(self.main)
        output_frame.grid(
            row=3, column=0,
            sticky="nsew", padx=25, pady=(0, 25)
        )

        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            output_frame,
            text="BOT ACTIVITY & ACTION PLANS",
            font=("Arial", 14, "bold")
        ).grid(
            row=0, column=0,
            sticky="w", padx=15, pady=10
        )

        self.output = ctk.CTkTextbox(
            output_frame,
            font=("Consolas", 12),
            wrap="word"
        )
        self.output.grid(
            row=1, column=0,
            sticky="nsew", padx=15, pady=(0, 15)
        )

        self.log("Dashboard initialized.")
        self.log("Local AI engine ready.")
        self.log("Waiting for instructions.")

    def log(self, message):
        self.output.insert("end", message + "\n")
        self.output.see("end")

    def set_status(self, message, color):
        self.status_label.configure(
            text=f"● {message}",
            text_color=color
        )

    # GENERATE PLAN
    def generate_plan(self):

        if self.bot_running:
            self.log("Stop the current automation first.")
            return

        instruction = self.instruction_input.get(
            "1.0", "end"
        ).strip()

        if not instruction:
            self.log("ERROR: Enter an instruction first.")
            return

        self.pending_actions = []
        self.plan_ready = False

        self.approve_button.configure(state="disabled")
        self.generate_button.configure(state="disabled")

        self.set_status("THINKING", "#eab308")
        self.log("\nAI is planning actions...")

        threading.Thread(
            target=self.plan_worker,
            args=(instruction,),
            daemon=True
        ).start()

    def plan_worker(self, instruction):

        try:
            actions = self.action_controller.generate_actions(
                instruction
            )

            if not isinstance(actions, list) or not actions:
                raise ValueError("AI returned an empty or invalid plan.")

            # Validate every action before displaying the plan.
            for action in actions:
                self.action_controller.validate_action(action)

            self.events.put(("plan", actions))

        except Exception as error:
            self.events.put(("error", str(error)))

    # APPROVE AND EXECUTE
    def approve_plan(self):

        if not self.pending_actions or not self.plan_ready:
            self.log("There is no approved action plan available.")
            return

        self.stop_requested = False
        self.bot_running = True
        self.plan_ready = False

        self.approve_button.configure(state="disabled")
        self.generate_button.configure(state="disabled")

        self.set_status("RUNNING", "#22c55e")
        self.log("\nExecuting approved action plan...")

        threading.Thread(
            target=self.execution_worker,
            daemon=True
        ).start()

    def execution_worker(self):

        engine = self.action_controller.engine

        try:
            engine.start()

            for index, action in enumerate(
                self.pending_actions, 1
            ):

                if self.stop_requested or not self.bot_running:
                    self.events.put(
                        ("log", "Automation stopped by user.")
                    )
                    break

                self.events.put(
                    ("log", f"Executing action {index}: {action}")
                )

                self.action_controller.execute_action(action)

            else:
                self.events.put(
                    ("log", "Action plan completed successfully!")
                )

        except Exception as error:
            self.events.put(
                ("error", f"Execution error: {error}")
            )

        finally:
            engine.stop()
            self.events.put(("finished", None))

    # STOP AUTOMATION
    def stop_bot(self):

        if not self.bot_running:
            self.log("No automation is currently running.")
            return

        self.stop_requested = True
        self.bot_running = False

        self.action_controller.engine.stop()

        self.set_status("STOPPING", "#ef4444")
        self.log("Stop requested. Finishing current action...")

    # PROCESS BACKGROUND EVENTS
    def process_events(self):

        try:
            while True:

                event, data = self.events.get_nowait()

                if event == "plan":

                    self.pending_actions = data
                    self.plan_ready = True

                    self.log("\nAI GENERATED ACTION PLAN:")

                    for index, action in enumerate(data, 1):
                        self.log(f"{index}. {action}")

                    self.log(
                        "\nReview the actions before approving."
                    )

                    self.approve_button.configure(
                        state="normal"
                    )

                    self.set_status("PLAN READY", "#eab308")

                elif event == "log":
                    self.log(data)

                elif event == "error":
                    self.log(f"ERROR: {data}")
                    self.set_status("ERROR", "#ef4444")
                    self.generate_button.configure(
                        state="normal"
                    )

                elif event == "finished":

                    self.bot_running = False
                    self.stop_requested = False

                    self.set_status("READY", "#22c55e")
                    self.generate_button.configure(
                        state="normal"
                    )

                    self.log("Automation session ended.")

        except queue.Empty:
            pass

        self.after(200, self.process_events)


if __name__ == "__main__":
    app = AutonomousCodingBotDashboard()
    app.mainloop()
