

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
            if y.speed > best:
                edge = y.other_end(self.id)

        return edge
