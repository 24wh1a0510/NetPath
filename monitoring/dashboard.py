import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the main NetPath folder to Python's path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)

from congestion_control.leaky_bucket import simulate_leaky_bucket


# --------------------------------------------------
# MONITORING CALCULATIONS
# --------------------------------------------------

def calculate_packet_loss(total_arrived, total_dropped):
    if total_arrived == 0:
        return 0.0

    return (total_dropped / total_arrived) * 100


def calculate_throughput(total_transmitted, simulation_time):
    if simulation_time <= 0:
        return 0.0

    return total_transmitted / simulation_time


def calculate_average_delay(total_delay, transmitted_packets):
    if transmitted_packets == 0:
        return 0.0

    return total_delay / transmitted_packets


def get_network_status(packet_loss, average_delay):

    # Project-defined thresholds
    if packet_loss > 5 or average_delay > 100:
        return "HIGH CONGESTION"

    elif packet_loss >= 2 or average_delay >= 50:
        return "MODERATE"

    else:
        return "NORMAL"


# --------------------------------------------------
# RUN MONITORING
# --------------------------------------------------

def run_monitoring():

    try:
        capacity = int(capacity_entry.get())
        output_rate = int(output_rate_entry.get())

        arrival_text = arrivals_entry.get()

        arrivals = [
            int(value.strip())
            for value in arrival_text.split(",")
        ]

        if capacity <= 0 or output_rate <= 0:
            raise ValueError

        if not arrivals:
            raise ValueError

        if any(value < 0 for value in arrivals):
            raise ValueError

    except ValueError:

        messagebox.showerror(
            "Invalid Input",
            "Please enter valid positive numbers.\n\n"
            "Example arrivals:\n"
            "8,1,4,0,3"
        )

        return

    # Run actual simulation
    results = simulate_leaky_bucket(
        capacity,
        output_rate,
        arrivals
    )

    # Get results
    total_arrived = results["total_arrived"]
    total_transmitted = results["total_transmitted"]
    total_dropped = results["total_dropped"]
    total_delay = results["total_delay"]

    simulation_time = len(arrivals)

    # Calculate monitoring metrics
    packet_loss = calculate_packet_loss(
        total_arrived,
        total_dropped
    )

    throughput = calculate_throughput(
        total_transmitted,
        simulation_time
    )

    average_delay = calculate_average_delay(
        total_delay,
        total_transmitted
    )

    network_status = get_network_status(
        packet_loss,
        average_delay
    )

    # Update dashboard
    arrived_value.config(
        text=str(total_arrived)
    )

    transmitted_value.config(
        text=str(total_transmitted)
    )

    dropped_value.config(
        text=str(total_dropped)
    )

    loss_value.config(
        text=f"{packet_loss:.2f}%"
    )

    throughput_value.config(
        text=f"{throughput:.2f} packets/time unit"
    )

    delay_value.config(
        text=f"{average_delay:.2f} time units"
    )

    status_value.config(
        text=network_status
    )

    # Time-wise data
    time_data = results["time"]
    dropped_data = results["dropped"]
    transmitted_data = results["transmitted"]
    queue_data = results["queue"]

    table_text.delete("1.0", tk.END)

    table_text.insert(
        tk.END,
        "Time   Arrived   Dropped   Transmitted   Queue\n"
    )

    table_text.insert(
        tk.END,
        "-" * 50 + "\n"
    )

    for i in range(len(time_data)):

        table_text.insert(
            tk.END,
            f"{time_data[i]:<7}"
            f"{arrivals[i]:<10}"
            f"{dropped_data[i]:<10}"
            f"{transmitted_data[i]:<14}"
            f"{queue_data[i]}\n"
        )


# --------------------------------------------------
# CREATE WINDOW
# --------------------------------------------------

window = tk.Tk()

window.title(
    "NetPath - Network Monitoring Dashboard"
)

window.geometry("850x650")


# --------------------------------------------------
# TITLE
# --------------------------------------------------

title = tk.Label(
    window,
    text="NETPATH MONITORING DASHBOARD",
    font=("Arial", 22, "bold")
)

title.pack(pady=15)


subtitle = tk.Label(
    window,
    text="Network Performance Monitoring & Analysis",
    font=("Arial", 12)
)

subtitle.pack(pady=5)


# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

input_frame = tk.Frame(window)

input_frame.pack(pady=15)


tk.Label(
    input_frame,
    text="Bucket Capacity:"
).grid(row=0, column=0, padx=10, pady=5)

capacity_entry = tk.Entry(input_frame, width=15)

capacity_entry.grid(row=0, column=1, padx=10, pady=5)

capacity_entry.insert(0, "5")


tk.Label(
    input_frame,
    text="Output Rate:"
).grid(row=1, column=0, padx=10, pady=5)

output_rate_entry = tk.Entry(input_frame, width=15)

output_rate_entry.grid(row=1, column=1, padx=10, pady=5)

output_rate_entry.insert(0, "2")


tk.Label(
    input_frame,
    text="Packet Arrivals:"
).grid(row=2, column=0, padx=10, pady=5)

arrivals_entry = tk.Entry(input_frame, width=30)

arrivals_entry.grid(row=2, column=1, padx=10, pady=5)

arrivals_entry.insert(0, "8,1,4,0,3")


# --------------------------------------------------
# RUN BUTTON
# --------------------------------------------------

run_button = tk.Button(
    window,
    text="RUN NETWORK ANALYSIS",
    command=run_monitoring,
    font=("Arial", 12, "bold"),
    padx=20,
    pady=8
)

run_button.pack(pady=10)


# --------------------------------------------------
# METRICS FRAME
# --------------------------------------------------

metrics_frame = tk.Frame(window)

metrics_frame.pack(pady=10)


# Row 1

tk.Label(
    metrics_frame,
    text="Packets Arrived",
    font=("Arial", 11, "bold")
).grid(row=0, column=0, padx=30, pady=5)

arrived_value = tk.Label(
    metrics_frame,
    text="-",
    font=("Arial", 14)
)

arrived_value.grid(
    row=1,
    column=0,
    padx=30,
    pady=5
)


tk.Label(
    metrics_frame,
    text="Packets Transmitted",
    font=("Arial", 11, "bold")
).grid(row=0, column=1, padx=30, pady=5)

transmitted_value = tk.Label(
    metrics_frame,
    text="-",
    font=("Arial", 14)
)

transmitted_value.grid(
    row=1,
    column=1,
    padx=30,
    pady=5
)


tk.Label(
    metrics_frame,
    text="Packets Dropped",
    font=("Arial", 11, "bold")
).grid(row=0, column=2, padx=30, pady=5)

dropped_value = tk.Label(
    metrics_frame,
    text="-",
    font=("Arial", 14)
)

dropped_value.grid(
    row=1,
    column=2,
    padx=30,
    pady=5
)


# Row 2

tk.Label(
    metrics_frame,
    text="Packet Loss",
    font=("Arial", 11, "bold")
).grid(row=2, column=0, padx=30, pady=15)

loss_value = tk.Label(
    metrics_frame,
    text="-",
    font=("Arial", 14)
)

loss_value.grid(
    row=3,
    column=0,
    padx=30,
    pady=5
)


tk.Label(
    metrics_frame,
    text="Throughput",
    font=("Arial", 11, "bold")
).grid(row=2, column=1, padx=30, pady=15)

throughput_value = tk.Label(
    metrics_frame,
    text="-",
    font=("Arial", 14)
)

throughput_value.grid(
    row=3,
    column=1,
    padx=30,
    pady=5
)


tk.Label(
    metrics_frame,
    text="Average Delay",
    font=("Arial", 11, "bold")
).grid(row=2, column=2, padx=30, pady=15)

delay_value = tk.Label(
    metrics_frame,
    text="-",
    font=("Arial", 14)
)

delay_value.grid(
    row=3,
    column=2,
    padx=30,
    pady=5
)


# --------------------------------------------------
# NETWORK STATUS
# --------------------------------------------------

tk.Label(
    window,
    text="NETWORK STATUS",
    font=("Arial", 12, "bold")
).pack(pady=5)

status_value = tk.Label(
    window,
    text="-",
    font=("Arial", 16, "bold")
)

status_value.pack(pady=5)


# --------------------------------------------------
# TIME-WISE DATA
# --------------------------------------------------

tk.Label(
    window,
    text="TIME-WISE MONITORING DATA",
    font=("Arial", 12, "bold")
).pack(pady=10)


table_text = tk.Text(
    window,
    width=65,
    height=8,
    font=("Courier New", 10)
)

table_text.pack(pady=5)


# --------------------------------------------------
# START DASHBOARD
# --------------------------------------------------

window.mainloop()