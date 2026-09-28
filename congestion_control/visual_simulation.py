
import tkinter as tk
from tkinter import messagebox
from collections import deque


class LeakyBucketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NetPath - Congestion Control")
        self.root.geometry("950x720")
        self.root.configure(bg="#101827")

        self.bucket = deque()
        self.capacity = 5
        self.rate = 2
        self.arrivals = []
        self.current_time = 0

        self.total_arrived = 0
        self.total_sent = 0
        self.total_dropped = 0

        title = tk.Label(
            root,
            text="LEAKY BUCKET CONGESTION CONTROL",
            font=("Arial", 20, "bold"),
            bg="#101827",
            fg="white"
        )
        title.pack(pady=15)

        controls = tk.Frame(root, bg="#101827")
        controls.pack(pady=5)

        tk.Label(
            controls, text="Capacity:", bg="#101827",
            fg="white"
        ).grid(row=0, column=0, padx=5)

        self.capacity_entry = tk.Entry(controls, width=7)
        self.capacity_entry.insert(0, "5")
        self.capacity_entry.grid(row=0, column=1, padx=5)

        tk.Label(
            controls, text="Output rate:", bg="#101827",
            fg="white"
        ).grid(row=0, column=2, padx=5)

        self.rate_entry = tk.Entry(controls, width=7)
        self.rate_entry.insert(0, "2")
        self.rate_entry.grid(row=0, column=3, padx=5)

        tk.Label(
            controls, text="Arrivals:", bg="#101827",
            fg="white"
        ).grid(row=1, column=0, padx=5, pady=12)

        self.arrivals_entry = tk.Entry(controls, width=40)
        self.arrivals_entry.insert(0, "8,1,4,0,3")
        self.arrivals_entry.grid(
            row=1, column=1, columnspan=3, padx=5
        )

        self.start_button = tk.Button(
            controls,
            text="Start Simulation",
            command=self.start_simulation,
            bg="#2563eb",
            fg="white",
            font=("Arial", 11, "bold")
        )
        self.start_button.grid(
            row=2, column=0, columnspan=4, pady=10
        )

        self.canvas = tk.Canvas(
            root, width=650, height=260,
            bg="#182338", highlightthickness=0
        )
        self.canvas.pack(pady=15)

        self.status_label = tk.Label(
            root, text="Enter values and start the simulation.",
            font=("Arial", 13, "bold"),
            bg="#101827", fg="#60a5fa"
        )
        self.status_label.pack(pady=5)

        self.stats_label = tk.Label(
            root, text="",
            font=("Consolas", 12),
            bg="#101827", fg="white",
            justify="left"
        )
        self.stats_label.pack(pady=10)

        self.draw_bucket()

    def start_simulation(self):
        try:
            capacity = int(self.capacity_entry.get())
            rate = int(self.rate_entry.get())

            arrivals = [
                int(x.strip())
                for x in self.arrivals_entry.get().split(",")
            ]

            if capacity <= 0 or rate <= 0:
                raise ValueError

            if not arrivals or any(x < 0 for x in arrivals):
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter positive capacity and rate, and "
                "non-negative comma-separated arrivals."
            )
            return

        self.capacity = capacity
        self.rate = rate
        self.arrivals = arrivals

        self.bucket = deque()
        self.current_time = 0
        self.total_arrived = 0
        self.total_sent = 0
        self.total_dropped = 0

        self.start_button.config(state="disabled")
        self.status_label.config(text="Simulation started")

        self.run_step()

    def run_step(self):
        if self.current_time >= len(self.arrivals):
            self.status_label.config(
                text="SIMULATION COMPLETED",
                fg="#4ade80"
            )
            self.start_button.config(state="normal")
            self.update_stats()
            return

        incoming = self.arrivals[self.current_time]
        self.total_arrived += incoming

        accepted = 0
        dropped = 0

        # Add incoming packets to the FIFO queue
        for i in range(incoming):
            if len(self.bucket) < self.capacity:
                self.bucket.append(
                    f"P{self.current_time + 1}-{i + 1}"
                )
                accepted += 1
            else:
                dropped += 1

        self.total_dropped += dropped

        # Transmit packets at the fixed output rate
        sent = min(self.rate, len(self.bucket))

        for _ in range(sent):
            self.bucket.popleft()

        self.total_sent += sent

        if dropped > 0:
            status = f"CONGESTION! {dropped} packet(s) dropped"
            color = "#f87171"
        elif len(self.bucket) == self.capacity:
            status = "BUCKET FULL"
            color = "#fbbf24"
        else:
            status = "NORMAL TRAFFIC"
            color = "#4ade80"

        self.status_label.config(
            text=f"Time {self.current_time + 1}: {status}",
            fg=color
        )

        self.draw_bucket(
            incoming, accepted, dropped, sent
        )
        self.update_stats()

        self.current_time += 1

        # Animate the next time unit
        self.root.after(1500, self.run_step)

    def draw_bucket(self, incoming=0, accepted=0,
                    dropped=0, sent=0):
        self.canvas.delete("all")

        self.canvas.create_text(
            325, 20, text="PACKET QUEUE",
            fill="white", font=("Arial", 15, "bold")
        )

        # Draw bucket outline
        self.canvas.create_rectangle(
            160, 55, 490, 225,
            outline="#60a5fa", width=3
        )

        # Draw packets inside the bucket
        for i, packet in enumerate(self.bucket):
            row = i // 4
            col = i % 4

            x = 185 + col * 75
            y = 75 + row * 55

            self.canvas.create_rectangle(
                x, y, x + 60, y + 40,
                fill="#2563eb", outline="white"
            )
            self.canvas.create_text(
                x + 30, y + 20,
                text=packet, fill="white",
                font=("Arial", 9, "bold")
            )

        # Show outgoing transmission
        self.canvas.create_text(
            325, 245,
            text=f"Outgoing: {sent} packet(s) | "
                 f"Incoming: {incoming} | "
                 f"Accepted: {accepted} | "
                 f"Dropped: {dropped}",
            fill="#93c5fd", font=("Arial", 11)
        )

    def update_stats(self):
        drop_percentage = (
            self.total_dropped / self.total_arrived * 100
            if self.total_arrived else 0
        )

        text = (
            f"Total Arrived: {self.total_arrived}       "
            f"Transmitted: {self.total_sent}\n"
            f"Total Dropped: {self.total_dropped}       "
            f"Remaining: {len(self.bucket)}\n"
            f"Drop Percentage: {drop_percentage:.2f}%"
        )

        self.stats_label.config(text=text)


if __name__ == "__main__":
    window = tk.Tk()
    app = LeakyBucketGUI(window)
    window.mainloop()