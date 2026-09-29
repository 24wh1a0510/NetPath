import sys
import os

# Add the main NetPath folder to Python's path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)


# Import routing module
try:
    from routing.routing import Graph, shortest_path
except ModuleNotFoundError:
    from routing import Graph, shortest_path


from congestion_control.leaky_bucket import simulate_leaky_bucket


# --------------------------------------------------
# MONITORING METRICS
# --------------------------------------------------

def calculate_packet_loss(total_arrived, total_dropped):
    if total_arrived == 0:
        return 0.0

    return (total_dropped / total_arrived) * 100


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
# CALCULATE MONITORING RESULTS
# --------------------------------------------------

def get_monitoring_results():

    results = simulate_leaky_bucket(
        capacity=5,
        output_rate=2,
        arrivals=[8, 1, 4, 0, 3]
    )

    packet_loss = calculate_packet_loss(
        results["total_arrived"],
        results["total_dropped"]
    )

    average_delay = calculate_average_delay(
        results["total_delay"],
        results["total_transmitted"]
    )

    status = get_network_status(
        packet_loss,
        average_delay
    )

    return {
        "packet_loss": packet_loss,
        "average_delay": average_delay,
        "status": status
    }


# --------------------------------------------------
# UPDATE LINK COST
# --------------------------------------------------

def update_link_cost(graph, source, destination, monitoring):

    # Get current link cost
    old_cost = graph.adj[source][destination]

    status = monitoring["status"]

    # Project-defined adaptive routing rule
    if status == "HIGH CONGESTION":
        new_cost = old_cost * 2

    elif status == "MODERATE":
        new_cost = old_cost * 1.5

    else:
        new_cost = old_cost

    graph.update_cost(
        source,
        destination,
        new_cost
    )

    return old_cost, new_cost


# --------------------------------------------------
# MAIN ADAPTIVE ROUTING DEMO
# --------------------------------------------------

def main():

    print("=" * 65)
    print("       NETPATH - ADAPTIVE ROUTING BRIDGE")
    print("=" * 65)

    # Load topology
    topology_path = os.path.join(
        PROJECT_ROOT,
        "routing",
        "topology.json"
    )

    graph = Graph.load(topology_path)

    # Get monitoring results
    monitoring = get_monitoring_results()

    print("\nMONITORING RESULTS")
    print("-" * 65)

    print(
        f"Packet Loss    : "
        f"{monitoring['packet_loss']:.2f}%"
    )

    print(
        f"Average Delay  : "
        f"{monitoring['average_delay']:.2f} time units"
    )

    print(
        f"Network Status : "
        f"{monitoring['status']}"
    )

    # Choose a link for demonstration
    source = "A"
    destination = "C"

    # Check original route
    old_cost, old_path = shortest_path(
        graph,
        "A",
        "F"
    )

    print("\nBEFORE ADAPTIVE UPDATE")
    print("-" * 65)

    print(
        f"Path A -> F : "
        f"{' -> '.join(old_path)}"
    )

    print(
        f"Path Cost   : "
        f"{old_cost}"
    )

    print(
        f"Link {source}-{destination} Cost : "
        f"{graph.adj[source][destination]}"
    )

    # Update link cost
    old_link_cost, new_link_cost = update_link_cost(
        graph,
        source,
        destination,
        monitoring
    )

    print("\nADAPTIVE ROUTING UPDATE")
    print("-" * 65)

    print(
        f"Link {source}-{destination}"
    )

    print(
        f"Old Cost : {old_link_cost}"
    )

    print(
        f"New Cost : {new_link_cost}"
    )

    # Calculate new route
    new_cost, new_path = shortest_path(
        graph,
        "A",
        "F"
    )

    print("\nAFTER ADAPTIVE UPDATE")
    print("-" * 65)

    print(
        f"Path A -> F : "
        f"{' -> '.join(new_path)}"
    )

    print(
        f"Path Cost   : "
        f"{new_cost}"
    )

    print("=" * 65)


if __name__ == "__main__":
    main()