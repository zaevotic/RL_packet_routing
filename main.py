import random
from network import Network
from packet import Status
import logger 


def main():
    print("=== RL Packet Routing Simulator ===")

    # Topology Setup
    use_default_net = input("Use default random network? (y/n) [default: y]: ").strip().lower()

    if use_default_net == "n":
        nodes_in = input("Enter number of nodes: ").strip()
        nodes = int(nodes_in) if nodes_in.isdigit() else 10

        edges_in = input("Enter number of edges: ").strip()
        edges = int(edges_in) if edges_in.isdigit() else 15

        net = Network(nodes=nodes, edges=edges)
    else:
        # Network's __init__ will randomly pick values if passed 0
        net = Network(nodes=0, edges=0)

    logger.graph_generated(net)
    print(f"Network initialized with {net.nodes} nodes and {net.edges} edges.\n")

    # Generation
    print("Choose traffic setup:")
    print("1. Standard random packets")
    print("2. Continuous traffic flow (Source -> Destination)")
    print("3. Both")
    choice = input("Enter choice (1/2/3) [default: 1]: ").strip()

    if choice == "2":
        src = int(input(f"Enter source node (0 to {net.nodes - 1}): "))
        dst = int(input(f"Enter destination node (0 to {net.nodes - 1}): "))
        count = int(input("Enter number of packets for flow: "))
        net.generate_traffic(A=src, B=dst, packets=count)
        logger.traffic_generated(net, src, dst, packets=count)

    elif choice == "3":
        # Add a traffic flow
        src = random.randint(0, net.nodes - 1)
        dst = random.randint(0, net.nodes - 1)
        while src == dst:
            dst = random.randint(0, net.nodes - 1)
        net.generate_traffic(A=src, B=dst, packets=10)
        logger.traffic_generated(net, src, dst, packets=10)

        # Add ad-hoc packets
        for _ in range(15):
            s = random.randint(0, net.nodes - 1)
            d = random.randint(0, net.nodes - 1)
            while s == d:
                d = random.randint(0, net.nodes - 1)
            net.generate_packet(A=s, B=d)
    else:
        # Default: generate simple random packets
        pkt_count = input("How many packets to generate? [default: 10]: ").strip()
        num_packets = int(pkt_count) if pkt_count.isdigit() else 10

        for _ in range(num_packets):
            s = random.randint(0, net.nodes - 1)
            d = random.randint(0, net.nodes - 1)
            while s == d:
                d = random.randint(0, net.nodes - 1)
            net.generate_packet(A=s, B=d)

    print(f"Total packets in queue: {len(net.packet_queue)}\n")

    # Sim
    mode = input("Run mode: (1) Run all steps, (2) Step-by-step interactive? [default: 1]: ").strip()

    steps_in = input("Maximum simulation steps to run? [default: 100]: ").strip()
    max_steps = int(steps_in) if steps_in.isdigit() else 100

    step_count = 0

    if mode == "2":
        while net.packet_queue and step_count < max_steps:
            step_count += 1
            cur_time, pkt_id = net.packet_queue[0]
            print(f"Step {step_count:03d} | Sim Time: {net.time} | Processing Pkt: {pkt_id}")
            net.next_packet()

            cont = input("Press [Enter] for next step or 'q' to stop: ").strip().lower()
            if cont == "q":
                break
    else:
        # Run straight through
        while net.packet_queue and step_count < max_steps:
            step_count += 1
            net.next_packet()

    print(f"\nSimulation ended at step {step_count}, current sim time: {net.time}")

    # Summary

    delivered = sum(1 for p in net.packet_list if p.status == Status.END)
    dead = sum(1 for p in net.packet_list if p.status == Status.DEAD)
    in_transit = len(net.packet_list) - delivered - dead

    print("\n--- Summary ---")
    print(f"Total Packets Created : {len(net.packet_list)}")
    print(f"Delivered             : {delivered}")
    print(f"Dropped / Dead        : {dead}")
    print(f"Still in Transit      : {in_transit}")
    print(f"Remaining in Queue    : {len(net.packet_queue)}")


if __name__ == "__main__":
    main()
