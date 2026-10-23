from enum import Enum

class Status(Enum):
    EDGE = 1
    NODE = 2
    QUEUE = 3
    PROCESSING = 4
    END = 5
    DEAD = 6

class Packet:
    def __init__(self, id, start, end, size, ttl = 50):
        self.id = id
        self.status = Status.NODE
        self.start = start
        self.end = end
        self.ttl = ttl
        self.size = size
        self.time_in_travel = 0
        self.history = [start]

    def __del__(self):
        self.status = Status.DEAD
