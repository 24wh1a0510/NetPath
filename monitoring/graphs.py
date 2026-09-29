import sys
import os
import matplotlib.pyplot as plt

# Add the main NetPath folder to Python's path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)

from congestion_control.leaky_bucket import simulate_leaky_bucket


# --------------------------------------------------
# RUN SIMULATION
# --------------------------------------------------

capacity = 5
output_rate = 2

arrivals = [8, 1, 4, 0, 3]

results = simulate_leaky_bucket(
    capacity,
    output_rate,
    arrivals
)


# --------------------------------------------------
# GET TIME-WISE DATA
# --------------------------------------------------

time = results["time"]
arrival_data = results["arrivals"]
dropped_data = results["dropped"]
transmitted_data = results["transmitted"]
queue_data = results["queue"]
delay_data = results["delay"]


# --------------------------------------------------
# GRAPH 1 - PACKET ARRIVALS AND DROPS
# --------------------------------------------------

plt.figure()

plt.plot(
    time,
    arrival_data,
    marker="o",
    label="Packets Arrived"
)

plt.plot(
    time,
    dropped_data,
    marker="o",
    label="Packets Dropped"
)

plt.title("Packet Arrival and Packet Loss Analysis")
plt.xlabel("Time Unit")
plt.ylabel("Number of Packets")

plt.xticks(time)

plt.legend()
plt.grid(True)

plt.show()


# --------------------------------------------------
# GRAPH 2 - THROUGHPUT
# --------------------------------------------------

plt.figure()

plt.plot(
    time,
    transmitted_data,
    marker="o"
)

plt.title("Network Throughput Over Time")
plt.xlabel("Time Unit")
plt.ylabel("Packets Transmitted")

plt.xticks(time)

plt.grid(True)

plt.show()


# --------------------------------------------------
# GRAPH 3 - QUEUE SIZE
# --------------------------------------------------

plt.figure()

plt.plot(
    time,
    queue_data,
    marker="o"
)

plt.title("Queue Size Over Time")
plt.xlabel("Time Unit")
plt.ylabel("Packets in Queue")

plt.xticks(time)

plt.grid(True)

plt.show()


# --------------------------------------------------
# GRAPH 4 - PACKET DELAY
# --------------------------------------------------

plt.figure()

plt.plot(
    time,
    delay_data,
    marker="o"
)

plt.title("Packet Delay Over Time")
plt.xlabel("Time Unit")
plt.ylabel("Delay (Time Units)")

plt.xticks(time)

plt.grid(True)

plt.show()


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

total_arrived = results["total_arrived"]
total_transmitted = results["total_transmitted"]
total_dropped = results["total_dropped"]
total_delay = results["total_delay"]

simulation_time = len(arrivals)

packet_loss = 0

if total_arrived > 0:
    packet_loss = (
        total_dropped / total_arrived
    ) * 100

throughput = 0

if simulation_time > 0:
    throughput = (
        total_transmitted / simulation_time
    )

average_delay = 0

if total_transmitted > 0:
    average_delay = (
        total_delay / total_transmitted
    )


print("\n" + "=" * 60)
print("             GRAPH ANALYSIS DATA")
print("=" * 60)

print(
    f"Packet Loss    : {packet_loss:.2f}%"
)

print(
    f"Throughput     : "
    f"{throughput:.2f} packets/time unit"
)

print(
    f"Average Delay  : "
    f"{average_delay:.2f} time units"
)

print("=" * 60)