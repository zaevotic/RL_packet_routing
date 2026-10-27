import json
import random
import sys
from bots import BOT_CATALOG, get_bot_class, DijkstraBot, MinHopBot, RLcraft
from config import Edge, Node
from network import Network
from packet import Status
import logger


def compute_stats(net, step_count):
    total = len(net.packet_list)
    delivered = sum(1 for p in net.packet_list if p.status == Status.END)
    dead = sum(1 for p in net.packet_list if p.status == Status.DEAD)
    in_transit = total - delivered - dead

    del_rate = round(delivered / total, 3) if total else 0.0
    del_pkts = [p for p in net.packet_list if p.status == Status.END and len(p.history_time) >= 2]

    latencies = []
    for p in del_pkts:
        valid_times = [t for t in p.history_time if t != -1]
        if len(valid_times) >= 2:
            lat = max(0, valid_times[-1] - valid_times[0])
            latencies.append(lat)
        elif len(valid_times) == 1:
            latencies.append(0)

    avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    avg_hops = round(sum(len(p.history_loc) - 1 for p in del_pkts) / len(del_pkts), 2) if del_pkts else 0.0

    return {
        "total": total,
        "delivered": delivered,
        "dead": dead,
        "in_transit": in_transit,
        "del_rate": del_rate,
        "avg_lat": avg_lat,
        "avg_hops": avg_hops,
        "step_count": step_count,
        "sim_time": net.time,
        "remaining_queue": len(net.packet_queue),
    }


def create_replicated_network(base_net, policy_name):
    """
    Creates an exact duplicate of base_net (same nodes, edges, bandwidth, speed,
    and identical packet workload), but attaches a new routing algorithm/policy.
    """
    net = Network(nodes=base_net.nodes, edges=len(base_net.edge_list), policy=policy_name)

    # Overwrite graph with exact replica of base_net
    DijkstraBot.clear_topology()
    MinHopBot.clear_topology()

    net.node_list = [Node(i, policy=policy_name) for i in range(base_net.nodes)]
    net.network = [[-1 for _ in range(base_net.nodes)] for _ in range(base_net.nodes)]
    net.edge_list = []

    for idx, e in enumerate(base_net.edge_list):
        new_edge = Edge(e.A, e.B, speed=e.speed, bandwidth=e.bandwidth)
        net.edge_list.append(new_edge)
        net.network[e.A][e.B] = idx
        net.network[e.B][e.A] = idx
        net.node_list[e.A].add_edge(e.B, new_edge)
        net.node_list[e.B].add_edge(e.A, new_edge)

    # Replicate identical packet traffic
    net.packet_list = []
    net.packet_queue = []
    net.packet_count = 0
    for p in base_net.packet_list:
        start_t = p.history_time[0] if p.history_time else 0
        net.generate_packet(A=p.history_loc[0], B=p.end_loc, size=p.size, ttl=p.ttl, start_time=start_t)

    return net


def run_simulation(net, max_steps=100, interactive=False):
    step_count = 0
    if interactive:
        while net.packet_queue and step_count < max_steps:
            step_count += 1
            cur_time, pkt_id = net.packet_queue[0]
            print(f"Step {step_count:03d} | Sim Time: {net.time} | Processing Pkt: {pkt_id}")
            net.next_packet()
            cont = input("Press [Enter] for next step or 'q' to stop: ").strip().lower()
            if cont == "q":
                break
    else:
        while net.packet_queue and step_count < max_steps:
            step_count += 1
            net.next_packet()

    return compute_stats(net, step_count)


def main():
    print("=== RL Packet Routing Simulator & Benchmark ===")

    auto_benchmark = any(arg in sys.argv for arg in ["--benchmark", "--all", "-b"])

    # 1. Routing Policy Selection
    print("Choose Mode / Routing Algorithm:")
    print("1. [Benchmark All Bots] Run all implemented bots & generate metrics.json [default]")
    for idx, bot_info in enumerate(BOT_CATALOG, 2):
        print(f"{idx}. {bot_info['name']} - {bot_info['description']}")

    if auto_benchmark:
        algo_choice = "1"
        print("Auto-benchmark flag detected. Selecting Option 1.")
    else:
        algo_choice = input(f"Enter choice (1-{len(BOT_CATALOG) + 1}) [default: 1]: ").strip()

    is_benchmark = (algo_choice in ("", "1"))

    if is_benchmark:
        chosen_policy_id = "rlcraft"
        chosen_policy_name = "Benchmark Suite (All Implemented Bots)"
    else:
        try:
            choice_num = int(algo_choice)
            idx = choice_num - 2
            if 0 <= idx < len(BOT_CATALOG):
                chosen_policy_id = BOT_CATALOG[idx]["id"]
                chosen_policy_name = BOT_CATALOG[idx]["name"]
            else:
                chosen_policy_id = "rlcraft"
                chosen_policy_name = BOT_CATALOG[0]["name"]
        except ValueError:
            chosen_policy_id = "rlcraft"
            chosen_policy_name = BOT_CATALOG[0]["name"]

    print(f"\nSelected Routing Mode: {chosen_policy_name}\n")

    # 2. Topology Setup
    use_default_net = input("Use default random network? (y/n) [default: y]: ").strip().lower()

    if use_default_net == "n":
        nodes_in = input("Enter number of nodes: ").strip()
        nodes = int(nodes_in) if nodes_in.isdigit() else 10

        edges_in = input("Enter number of edges: ").strip()
        edges = int(edges_in) if edges_in.isdigit() else 15

        net = Network(nodes=nodes, edges=edges, policy=chosen_policy_id)
    else:
        net = Network(nodes=0, edges=0, policy=chosen_policy_id)

    logger.graph_generated(net)
    print(f"Network initialized with {net.nodes} nodes and {net.edges} edges.\n")

    # 3. Traffic Generation
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
        src = random.randint(0, net.nodes - 1)
        dst = random.randint(0, net.nodes - 1)
        while src == dst:
            dst = random.randint(0, net.nodes - 1)
        net.generate_traffic(A=src, B=dst, packets=10)
        logger.traffic_generated(net, src, dst, packets=10)

        for _ in range(15):
            s = random.randint(0, net.nodes - 1)
            d = random.randint(0, net.nodes - 1)
            while s == d:
                d = random.randint(0, net.nodes - 1)
            net.generate_packet(A=s, B=d, start_time=random.randint(0, 30))
    else:
        pkt_count = input("How many packets to generate? [default: 10]: ").strip()
        num_packets = int(pkt_count) if pkt_count.isdigit() else 10

        rand_time = input("Randomize packet entry times across simulation? (y/n) [default: y]: ").strip().lower()
        spread = max(10, num_packets * 2)

        for i in range(num_packets):
            s = random.randint(0, net.nodes - 1)
            d = random.randint(0, net.nodes - 1)
            while s == d:
                d = random.randint(0, net.nodes - 1)
            t = random.randint(0, spread) if rand_time != "n" else 0
            net.generate_packet(A=s, B=d, start_time=t)

    print(f"Total packets in queue: {len(net.packet_queue)}\n")

    # 4. Simulation Execution
    steps_in = input("Maximum simulation steps to run? [default: 100]: ").strip()
    max_steps = int(steps_in) if steps_in.isdigit() else 100

    if not is_benchmark:
        # Single bot execution
        mode = input("Run mode: (1) Run all steps, (2) Step-by-step interactive? [default: 1]: ").strip()
        interactive = (mode == "2")

        stats = run_simulation(net, max_steps=max_steps, interactive=interactive)

        print(f"\nSimulation ended at step {stats['step_count']}, current sim time: {stats['sim_time']}")
        print("\n--- Summary ---")
        print(f"Total Packets Created : {stats['total']}")
        print(f"Delivered             : {stats['delivered']}")
        print(f"Dropped / Dead        : {stats['dead']}")
        print(f"Still in Transit      : {stats['in_transit']}")
        print(f"Remaining in Queue    : {stats['remaining_queue']}")
        print(f"Delivery Rate         : {round(stats['del_rate'] * 100, 1)}%")
        print(f"Average Latency       : {stats['avg_lat']} ticks")
        print(f"Average Hops          : {stats['avg_hops']}")

        # Preserve previous benchmark metrics if available for non-active bots
        existing_baselines = {}
        try:
            with open("metrics.json", "r", encoding="utf-8") as f:
                old_data = json.load(f)
                for b in old_data.get("baselines", []):
                    existing_baselines[b["name"]] = b
        except Exception:
            pass

        baselines = []
        for b in BOT_CATALOG:
            if b["id"] == chosen_policy_id:
                baselines.append({
                    "name": b["name"],
                    "delivery_rate": stats["del_rate"],
                    "avg_latency": stats["avg_lat"],
                    "avg_hops": stats["avg_hops"],
                    "status": "Active (Current Run)"
                })
            elif b["name"] in existing_baselines:
                old_entry = dict(existing_baselines[b["name"]])
                old_entry["status"] = "Benchmarked"
                baselines.append(old_entry)
            else:
                baselines.append({
                    "name": b["name"],
                    "delivery_rate": 0.0,
                    "avg_latency": 0.0,
                    "avg_hops": 0.0,
                    "status": "Implemented"
                })

        metrics_data = {
            "training": RLcraft.get_training_metrics(),
            "baselines": baselines
        }

    else:
        # Full Benchmark Suite across all implemented bots on identical network & traffic
        print("\n" + "=" * 80)
        print("RUNNING BENCHMARK SUITE ACROSS ALL IMPLEMENTED AGENTS")
        print("=" * 80)

        benchmark_results = []

        # Run primary algorithm (RLcraft) with trace logging enabled
        logger.ENABLE_TRACE = True
        rl_stats = run_simulation(net, max_steps=max_steps)
        benchmark_results.append((BOT_CATALOG[0], rl_stats))
        print(f"✓ Completed {BOT_CATALOG[0]['name']}")

        # Disable trace logging for replica runs to preserve the primary visualizer trace
        logger.ENABLE_TRACE = False

        for b in BOT_CATALOG[1:]:
            clone_net = create_replicated_network(net, b["id"])
            stats = run_simulation(clone_net, max_steps=max_steps)
            benchmark_results.append((b, stats))
            print(f"✓ Completed {b['name']}")

        logger.ENABLE_TRACE = True

        # Print comparison table
        print("\n" + "=" * 90)
        print(f"{'Algorithm':<28} | {'Delivery Rate':<14} | {'Avg Latency':<13} | {'Avg Hops':<10} | {'Delivered/Total'}")
        print("-" * 90)

        baselines = []
        for b, st in benchmark_results:
            del_pct = f"{round(st['del_rate'] * 100, 1)}%"
            lat_str = f"{st['avg_lat']} ticks"
            ratio = f"{st['delivered']}/{st['total']}"
            print(f"{b['name']:<28} | {del_pct:<14} | {lat_str:<13} | {st['avg_hops']:<10} | {ratio}")

            baselines.append({
                "name": b["name"],
                "delivery_rate": st["del_rate"],
                "avg_latency": st["avg_lat"],
                "avg_hops": st["avg_hops"],
                "status": "Benchmarked"
            })

        print("=" * 90)

        metrics_data = {
            "training": RLcraft.get_training_metrics(),
            "baselines": baselines
        }

    # Save metrics.json
    try:
        with open("metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2)
        print("\n[Metrics] Successfully generated metrics.json with all implemented agents.")
        print("[Visualizer] In visualizer.html, click the Analytics tab to view or click 'Fetch metrics.json' to reload.")
    except Exception as e:
        print(f"\n[Metrics Error] {e}")


if __name__ == "__main__":
    main()
