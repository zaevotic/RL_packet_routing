import json
import random
from pathlib import Path

DATA_DIR = Path("Data/Bots")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# RL Hyperparameters
ALPHA = 0.1       # Learning rate
GAMMA = 0.95      # Discount factor
EPSILON = 0.15    # Exploration rate

# Reward and Penalty values
REWARD_TARGET_REACHED = 100.0
PENALTY_LOOP_DROPPED = -100.0
PENALTY_PER_HOP = -1.5
PENALTY_PER_TIME = -0.1


class Greedy:
    def __init__(self, id):
        self.neighbours = {}
        self.id = id

    def add_neighbor(self, B, edge):
        self.neighbours[B] = edge

    def run(self, packet=None):
        best = 0
        edge = -1
        for x, y in self.neighbours.items():
            if y.speed > best:
                best = y.speed
                edge = y.other_end(self.id)
        if edge == -1 and self.neighbours:
            edge = random.choice(list(self.neighbours.keys()))
        return edge


class Bot:
    """
    Tabular Q-Learning Bot for Packet Routing.
    Q-Matrix: Destination x Outgoing Neighbor Edge/Node.
    Persisted to Data/Bots/node_{id}.json to conserve memory and preserve learning.
    """
    instances = {}

    def __init__(self, id, alpha=ALPHA, gamma=GAMMA, epsilon=EPSILON):
        self.id = id
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.neighbours = {}

        self.file_path = DATA_DIR / f"node_{self.id}.json"
        self.q_table = self.load()
        Bot.instances[self.id] = self

    def add_neighbor(self, B, edge):
        self.neighbours[B] = edge

    def load(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {int(dst): {int(nh): float(q) for nh, q in nhs.items()} for dst, nhs in data.items()}
            except Exception:
                pass
        return {}

    def save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.q_table, f, indent=2)
        except Exception:
            pass

    def get_q(self, dst, next_hop):
        return self.q_table.get(dst, {}).get(next_hop, 0.0)

    def set_q(self, dst, next_hop, val):
        if dst not in self.q_table:
            self.q_table[dst] = {}
        self.q_table[dst][next_hop] = val

    def run(self, packet):
        dst = packet.end_loc
        candidates = list(self.neighbours.keys())
        if not candidates:
            return -1

        # Direct link to destination is immediately chosen if adjacent
        if dst in self.neighbours:
            return dst

        # Epsilon-greedy exploration
        if random.random() < self.epsilon:
            return random.choice(candidates)

        # Greedy exploitation: select neighbor with maximum Q-value for destination
        best_q = -float("inf")
        best_actions = []
        for c in candidates:
            q = self.get_q(dst, c)
            if q > best_q:
                best_q = q
                best_actions = [c]
            elif q == best_q:
                best_actions.append(c)

        return random.choice(best_actions)

    def learn(self, dst, next_hop, target_return):
        current_q = self.get_q(dst, next_hop)
        new_q = current_q + self.alpha * (target_return - current_q)
        self.set_q(dst, next_hop, round(new_q, 4))

    @classmethod
    def reward_trajectory(cls, packet, status="reached"):
        """
        Delayed Trajectory Replay:
        Computes overall return based on arrival success, travel time, and hop count,
        then backpropagates discounted credit to all nodes along the packet's path.
        """
        locs = getattr(packet, "history_loc", [])
        times = getattr(packet, "history_time", [])
        dst = getattr(packet, "end_loc", None)

        if len(locs) < 2 or dst is None:
            return

        total_hops = len(locs) - 1
        valid_times = [t for t in times if t != -1]
        start_t = valid_times[0] if valid_times else 0
        end_t = valid_times[-1] if valid_times else 0
        total_time = max(0, end_t - start_t)

        # Reward / penalty calculation
        if status == "reached":
            r_base = REWARD_TARGET_REACHED
        else:
            r_base = PENALTY_LOOP_DROPPED

        total_reward = r_base + (PENALTY_PER_HOP * total_hops) + (PENALTY_PER_TIME * total_time)

        # Backpropagate along path
        for i in range(total_hops):
            node_u = locs[i]
            node_v = locs[i + 1]

            discount = GAMMA ** (total_hops - 1 - i)
            g_i = total_reward * discount

            bot = cls.instances.get(node_u)
            if bot is not None:
                bot.learn(dst, node_v, g_i)
                bot.save()