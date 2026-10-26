from enum import Enum

class Status(Enum):
    EDGE = 1
    NODE = 2
    QUEUE = 3
    PROCESSING = 4
    END = 5
    DEAD = 6

class Packet:
    def __init__(self, id, start_loc, end_loc, size, start_time, ttl = 50):
        self.id = id
        self.status = Status.NODE
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.ttl = ttl
        self.size = size
        self.time_in_travel = 0
        
        self.history_loc = [start_loc]
        self.history_time = [start_time]

    def reached(self):
        self.history_time.append(-1)    # So we can filter out this from packet_queue
        self.status = Status.END

    def sent(self, C, time):
        self.history_loc.append(C)
        self.history_time.append(time)

    def __del__(self):
        self.status = Status.DEAD   # This should never be run
