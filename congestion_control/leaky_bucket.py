
from collections import deque


def leaky_bucket():
    print("=" * 60)
    print("       CONGESTION CONTROL - LEAKY BUCKET")
    print("=" * 60)

    # Network parameters
    capacity = int(input("Enter bucket capacity (packets): "))
    output_rate = int(input("Enter output rate (packets per time unit): "))
    total_time = int(input("Enter number of time units: "))

    if capacity <= 0 or output_rate <= 0 or total_time <= 0:
        print("All values must be positive.")
        return

    # Queue stores packets waiting for transmission
    bucket = deque()

    total_arrived = 0
    total_transmitted = 0
    total_dropped = 0

    print("\nEnter packet arrivals for each time unit.")
    print("Example: 5 means 5 packets arrive at that time.\n")

    arrivals = []

    for t in range(total_time):
        packets = int(input(f"Packets arriving at time {t + 1}: "))
        if packets < 0:
            print("Packet arrivals cannot be negative.")
            return
        arrivals.append(packets)

    print("\n" + "=" * 85)
    print(f"{'Time':<8}{'Arrivals':<12}{'Accepted':<12}"
          f"{'Dropped':<12}{'Sent':<10}{'Queue':<12}{'Status'}")
    print("=" * 85)

    for t in range(total_time):
        incoming = arrivals[t]
        total_arrived += incoming

        accepted = 0
        dropped = 0

        # Step 1: Packets enter the bucket
        for packet in range(incoming):
            if len(bucket) < capacity:
                bucket.append(f"P{t + 1}-{packet + 1}")
                accepted += 1
            else:
                dropped += 1

        total_dropped += dropped

        # Step 2: Packets leak out at a fixed rate
        sent = min(output_rate, len(bucket))

        for _ in range(sent):
            bucket.popleft()

        total_transmitted += sent

        # Step 3: Display current network state
        if dropped > 0:
            status = "CONGESTION - PACKETS DROPPED"
        elif len(bucket) == capacity:
            status = "BUCKET FULL"
        else:
            status = "NORMAL"

        print(f"{t + 1:<8}{incoming:<12}{accepted:<12}"
              f"{dropped:<12}{sent:<10}{len(bucket):<12}{status}")

    # Summary
    print("\n" + "=" * 60)
    print("             CONGESTION RESULTS")
    print("=" * 60)

    print("Total packets arrived    :", total_arrived)
    print("Total packets transmitted:", total_transmitted)
    print("Total packets dropped    :", total_dropped)
    print("Packets remaining        :", len(bucket))
    print("Bucket capacity          :", capacity)
    print("Output rate              :", output_rate)

    if total_arrived > 0:
        drop_percentage = (total_dropped / total_arrived) * 100
        print(f"Packet drop percentage   : {drop_percentage:.2f}%")

    if total_dropped > 0:
        print("Network status           : CONGESTION DETECTED")
    else:
        print("Network status           : NO PACKET DROPS")

    print("=" * 60)


if __name__ == "__main__":
    leaky_bucket()