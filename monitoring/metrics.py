import sys
import os

# Add the main NetPath folder to Python's path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)

from congestion_control.leaky_bucket import simulate_leaky_bucket


# --------------------------------------------------
# PACKET LOSS
# --------------------------------------------------

def calculate_packet_loss(total_arrived, total_dropped):
    if total_arrived == 0:
        return 0.0

    return (total_dropped / total_arrived) * 100


# --------------------------------------------------
# THROUGHPUT
# --------------------------------------------------

def calculate_throughput(total_transmitted, simulation_time):
    if simulation_time <= 0:
        return 0.0

    return total_transmitted / simulation_time


# --------------------------------------------------
# AVERAGE DELAY
# --------------------------------------------------

def calculate_average_delay(total_delay, transmitted_packets):
    if transmitted_packets == 0:
        return 0.0

    return total_delay / transmitted_packets


# --------------------------------------------------
# NETWORK STATUS
# --------------------------------------------------

def get_network_status(packet_loss, average_delay):

    # Project-defined thresholds
    if packet_loss > 5 or average_delay > 100:
        return "HIGH CONGESTION"

    elif packet_loss >= 2 or average_delay >= 50:
        return "MODERATE"

    else:
        return "NORMAL"


# --------------------------------------------------
# CALCULATE ALL METRICS
# --------------------------------------------------

def calculate_metrics(
    total_arrived,
    total_dropped,
    total_transmitted,
    simulation_time,
    total_delay
):

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

    return {
        "packet_loss": packet_loss,
        "throughput": throughput,
        "average_delay": average_delay,
        "network_status": network_status
    }


# --------------------------------------------------
# RUN CONGESTION SIMULATION
# --------------------------------------------------

results = simulate_leaky_bucket(
    capacity=5,
    output_rate=2,
    arrivals=[8, 1, 4, 0, 3]
)


# --------------------------------------------------
# GET ACTUAL DELAY
# --------------------------------------------------

total_delay = results["total_delay"]


# --------------------------------------------------
# MONITORING ANALYSIS
# --------------------------------------------------

monitoring_results = calculate_metrics(
    total_arrived=results["total_arrived"],
    total_dropped=results["total_dropped"],
    total_transmitted=results["total_transmitted"],
    simulation_time=5,
    total_delay=total_delay
)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("\n" + "=" * 60)
print("             NETWORK MONITORING RESULTS")
print("=" * 60)

print(
    "Total packets arrived    :",
    results["total_arrived"]
)

print(
    "Total packets transmitted:",
    results["total_transmitted"]
)

print(
    "Total packets dropped    :",
    results["total_dropped"]
)

print(
    "Total packet delay       :",
    total_delay,
    "time units"
)

print(
    "Packet Loss              :",
    f"{monitoring_results['packet_loss']:.2f}%"
)

print(
    "Throughput               :",
    f"{monitoring_results['throughput']:.2f}",
    "packets/time unit"
)

print(
    "Average Delay            :",
    f"{monitoring_results['average_delay']:.2f}",
    "time units"
)

print(
    "Network Status           :",
    monitoring_results["network_status"]
)

print("=" * 60)