import json
from pathlib import Path
import random

class Greedy:

    def __init__(self, id):
        self.neighbours = {}
        self.id = id

    def add_neighbor(self, B, edge):
        self.neighbours[B] = edge

    def run(self):
        best = 0
        edge = -1
        for x,y in self.neighbours.items():
            while edge == -1:
                if random.randint(0,3) == 3:
                    edge = y.other_end(self.id)

        return edge

class Bot:

    def __init__(self, id):
        self.id = id 
        self.neighbours = {}

        folder = Path("Data/Bots")
        folder.mkdir(parents=True, exist_ok = True)

        self.file_path = folder / "matrices.json"

        # Learning Rate (L)
        # Expected Reward (Q)

    def add_neighbor(self, B, edge):
        self.neighbours[B] = edge

    def run(self, packet):
        destination = packet.end_loc
        
    