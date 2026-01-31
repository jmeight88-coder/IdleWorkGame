import time
import pickle
import tkinter as tk
from tkinter import messagebox
earned=0

class IdleWorkGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Idle Study Game")
        # Core game state
        file_path = 'data.pkl'
        try:
            with open(file_path, 'rb') as file:
                self.points = pickle.load(file)
        except FileNotFoundError:
            self.points=0
            with open('data.pkl', 'wb') as f:
                pickle.dump(self.points, f)

        self.base_rate = 1.0  # base points per 30 minutes per work unit
        self.multiplier = 1.0
        self.session_start_time = None

        # Shop items: name -> (cost, multiplier_increase)
        self.shop_items = [
            {"name": "Small Multiplier (+0.2x)", "cost": 50, "mult_increase": 0.2},
            {"name": "Medium Multiplier (+0.7x)", "cost": 150, "mult_increase": 0.7},
            {"name": "Big Multiplier (+3.0x)", "cost": 450, "mult_increase": 3.0},
            {"name": "Super Multiplier (+7.0x)", "cost": 1300, "mult_increase": 7.0},
            {"name": "Mega Multiplier (+25.0x)", "cost": 5000, "mult_increase": 25.0},
            {"name": "Ultra Multiplier (+100x)", "cost": 15000, "mult_increase": 100.0},
        ]

        self.build_ui()
        self.update_ui()

    def build_ui(self):
        # Top frame: stats
        stats_frame = tk.Frame(self.root, padx=10, pady=10)
        stats_frame.pack(fill="x")

        self.points_label = tk.Label(stats_frame, text="Points: 0")
        self.points_label.grid(row=0, column=0, sticky="w")

        self.mult_label = tk.Label(stats_frame, text="Multiplier: 1.0x")
        self.mult_label.grid(row=1, column=0, sticky="w")

        # Middle frame: Work time controls
        time_frame = tk.LabelFrame(self.root, text="Work Time", padx=10, pady=10)
        time_frame.pack(fill="x", padx=10, pady=5)
        self.work_time_label = tk.Label(time_frame, text="Set your start time and your end time (24hr format): ")
        self.work_time_label.grid(row=0, column=0, columnspan=4, sticky="w")
        # Start hour dropdown
        self.start_hour_var = tk.StringVar(value="1")
        self.start_hour_dropdown = tk.OptionMenu(time_frame, self.start_hour_var, *[str(i) for i in range(1, 25)])
        self.start_hour_dropdown.grid(row=1, column=1, padx=5, sticky="w")
        # End hour dropdown
        self.end_hour_var = tk.StringVar(value="1")
        self.end_hour_dropdown = tk.OptionMenu(time_frame, self.end_hour_var, *[str(i) for i in range(1, 25)])
        self.end_hour_dropdown.grid(row=1, column=2, padx=5, sticky="w")

        # Middle frame: work session controls
        work_frame = tk.LabelFrame(self.root, text="Work Session", padx=10, pady=10)
        
        work_frame.pack(fill="x", padx=10, pady=5)

        self.session_status_label = tk.Label(work_frame, text="No active session.")
        self.session_status_label.grid(row=0, column=0, columnspan=3, sticky="w")

        # ...removed work intensity UI...

        self.start_button = tk.Button(work_frame, text="Start Session", command=self.start_session)
        self.start_button.grid(row=2, column=0, pady=5, sticky="we")

        self.checkin_button = tk.Button(work_frame, text="Check In / Claim Points", command=self.check_in, state="disabled")
        self.checkin_button.grid(row=2, column=1, pady=5, sticky="we")

        self.time_worked_label = tk.Label(work_frame, text="Time worked: 0 min")
        self.time_worked_label.grid(row=3, column=0, columnspan=3, sticky="w")
        
        # Bottom frame: shop
        shop_frame = tk.LabelFrame(self.root, text="Shop", padx=10, pady=10)
        shop_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.shop_buttons = []
        for i, item in enumerate(self.shop_items):
            item_label = tk.Label(shop_frame, text=f"{item['name']} - Cost: {item['cost']} pts")
            item_label.grid(row=i, column=0, sticky="w")

            btn = tk.Button(shop_frame, text="Buy", command=lambda idx=i: self.buy_item(idx))
            btn.grid(row=i, column=1, padx=5, sticky="e")
            self.shop_buttons.append(btn)

        # Periodic UI update (for time worked display)
        self.root.after(1000, self.tick)

    def start_session(self):
        if self.session_start_time is not None:
            messagebox.showinfo("Session Active", "You already have an active session.")
            return
        current_hour = time.localtime().tm_hour
        start_hour = int(self.start_hour_var.get())
        end_hour = int(self.end_hour_var.get())
        if start_hour <= current_hour <= end_hour:
            self.session_start_time = time.time()
            self.session_status_label.config(text="Session active. Keep working!")
            self.checkin_button.config(state="normal")
            self.start_button.config(state="disabled")
        else:
          self.session_status_label.config(text="You are outside your designated work time! You cannot start a work session now.")


    def check_in(self):
        if self.session_start_time is None:
            messagebox.showinfo("No Session", "Start a session before checking in.")
            return
       
        now = time.time()
        elapsed_seconds = now - self.session_start_time
        elapsed_minutes = elapsed_seconds / 60.0

        # Reset session
        self.session_start_time = None
        self.session_status_label.config(text="No active session.")
        self.checkin_button.config(state="disabled")
        self.start_button.config(state="normal")
        self.time_worked_label.config(text="Time worked: 0 min")

        # Calculate points:
        # base_rate points per 30 minutes, scaled by multiplier
        time_factor = elapsed_minutes / 1
        earned = self.base_rate * time_factor * self.multiplier

        if earned <= 0:
            with open('data.pkl', 'wb') as f:
                pickle.dump(self.points, f)
            messagebox.showinfo("No Points", "Not enough time worked to earn points. Try at least a few minutes.")
            return

        self.points += earned
        with open('data.pkl', 'wb') as f:
            pickle.dump(self.points, f)
        messagebox.showinfo("Check-in Complete", f"You worked for {elapsed_minutes:.1f} minutes\n"
                                                 f"Multiplier: {self.multiplier:.1f}x\n\n"
                                                 f"Points earned: {earned:.1f}\n"
                                                 f"good work!")

        self.update_ui()

    def buy_item(self, idx):
        item = self.shop_items[idx]
        cost = item["cost"]
        if self.points < cost:
            messagebox.showinfo("Not enough points", "You don't have enough points for this upgrade.")
            return

        self.points -= cost
        self.multiplier += item["mult_increase"]
        messagebox.showinfo("Upgrade purchased", f"You bought: {item['name']}\n"
                                                 f"New multiplier: {self.multiplier:.1f}x")
        self.update_ui()

    def update_ui(self):
        self.points_label.config(text=f"Points: {self.points:.1f}")
        self.mult_label.config(text=f"Multiplier: {self.multiplier:.1f}x")

    def tick(self):
        # Update time worked display if session active
        if self.session_start_time is not None:
            elapsed_seconds = time.time() - self.session_start_time
            elapsed_minutes = int(elapsed_seconds // 60)
            self.time_worked_label.config(text=f"Time worked: {elapsed_minutes} min")
        self.root.after(1000, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    app = IdleWorkGame(root)
    root.mainloop()
