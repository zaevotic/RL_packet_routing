# RL Packet Routing

A discrete-event packet routing simulator that compares a tabular reinforcement learning agent (**RLcraft**) with classic routing baselines, plus a browser visualizer and analytics dashboard.

## Features

- Randomly generated undirected network (nodes, edges, per-edge speed and bandwidth, queueing).
- Packet traffic with randomized entry times, loop detection and drops.
- Six routing agents:

| Agent | Registry keys | Description |
| :--- | :--- | :--- |
| RLcraft | `rl`, `rlcraft`, `q_learning` | Per-node destination x next-hop table, epsilon-greedy, delayed trajectory-return updates |
| Dijkstra | `dijkstra`, `shortest_path` | Link-state shortest path, weight `10 / max(1, speed)` |
| Min-Hop | `min_hop`, `bfs` | BFS shortest hop count |
| Greedy | `greedy`, `greedy_bot` | Picks the neighbor with the fastest link |
| Random Walk | `random`, `random_walk` | Random neighbor, avoids immediate bounce-back |
| Least Congested | `least_congested` | Picks the lowest `capacity / bandwidth` link |

## Requirements

- Python 3.8+ (developed on 3.14)
- No third-party packages (standard library only)
- A modern web browser for `visualizer.html`

## Quick start

```bash
git clone https://github.com/zaevotic/RL_packet_routing.git
cd RL_packet_routing
python3 main.py
```

Run from the repository root: learned tables are stored in the relative path `Data/Bots/`.

### Benchmark all agents (recommended)

```bash
python3 main.py --benchmark     # also: --all or -b
```

This runs RLcraft first (with trace logging), then replays the identical network and packet workload for every baseline. It writes:

- `metrics.json`: training series and per-agent delivery rate, latency and hops
- `trace.json`: event trace of the RLcraft run for the visualizer

### Interactive mode

Running `python3 main.py` without flags prompts for:

1. Mode: `1` benchmark all agents (default), or `2`-`7` for a single agent.
2. Network: default random network, or custom node and edge counts.
3. Traffic: random packets, continuous flow between two nodes, or both.
4. Number of packets and whether to randomize entry times.
5. Maximum simulation steps (default `100`; raise it, e.g. `5000`, so all packets finish).
6. Single-agent mode only: run all steps, or step through interactively.

## Visualizer and analytics

1. Open `visualizer.html` in a browser.
2. **Replay** tab: click **Upload trace.json** and select `trace.json`. Use play, scrub and speed controls. Simultaneous events are grouped in the side stream.
3. **Analytics** tab: click **Upload metrics.json** and select `metrics.json`. This shows agent comparison and RLcraft training charts.
4. If the files sit next to `visualizer.html` and the page is served over HTTP (e.g. `python3 -m http.server`), it can load them automatically.
5. **Demo trace** shows a built-in sample (synthetic data, not experiment output).

## RLcraft details

- **State:** packet destination at the current node (node identity is implicit; each node has its own table).
- **Actions:** outgoing neighbor nodes. A directly adjacent destination is always chosen.
- **Policy:** epsilon-greedy with `EPSILON = 0.15`; ties broken randomly.
- **Reward (once per packet, on termination):** `R = (+100 if delivered else -100) - 1.5 * hops - 0.1 * travel_time`
- **Update:** for hop `i` of `H`, `G_i = R * GAMMA^(H-1-i)` and `Q(dst, next) += ALPHA * (G_i - Q(dst, next))`, with `ALPHA = 0.1`, `GAMMA = 0.95`. This is a Monte Carlo trajectory-return update, not one-step Q-learning.
- **Persistence:** tables are saved to `Data/Bots/node_{id}.json` after each update and reloaded on start.

Hyperparameters and rewards are constants at the top of [bots.py](bots.py).

## Resetting learning

Learned tables persist between runs. For a fresh agent, delete them:

```bash
rm -rf Data/Bots
```

## Project layout

| File | Purpose |
| :--- | :--- |
| `main.py` | CLI entry point, benchmark runner, metrics export |
| `bots.py` | RLcraft, baselines, bot registry and catalog |
| `config.py` | `Node` (routing and loop handling) and `Edge` (queueing and delay) |
| `network.py` | Topology and traffic generation, event loop |
| `packet.py` | Packet state and history |
| `logger.py` | Logging and `trace.json` event output |
| `visualizer.html` | Replay and analytics UI |
| `metrics.json`, `trace.json` | Generated outputs (git-ignored) |
| `Data/Bots/` | Persisted Q-tables (git-ignored) |

## Adding a new routing agent

1. Create a class in `bots.py` with `__init__(self, id)`, `add_neighbor(self, B, edge)` and `run(self, packet)`. `run` returns the next-hop node id, or `-1` if none.
2. Register it in `BOT_REGISTRY` and add an entry to `BOT_CATALOG`.
3. Re-run `python3 main.py --benchmark`. It is included automatically.

## Notes and limitations

- The topology and traffic are random and no seed is set, so results vary between runs. Add `random.seed(...)` in `main.py` for reproducibility.
- RLcraft does not observe queues or congestion, so its state is partially observable.
- Output files and learned tables are git-ignored, so a fresh clone starts untrained.
- There are no automated tests.
