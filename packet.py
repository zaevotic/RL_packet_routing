from enum import Enum
import logger

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
        logger.packet_created(self)

    def reached(self, time=None):
        if time is not None:
            self.history_time.append(time)
        self.history_time.append(-1)    # So we can filter out this from packet_queue
        self.status = Status.END
        t = time if time is not None else (self.history_time[-2] if len(self.history_time) > 1 and self.history_time[-2] != -1 else 0)
        logger.packet_delivered(self, t)

    def sent(self, C, time):
        prev = self.history_loc[-1] if self.history_loc else None
        self.history_loc.append(C)
        self.history_time.append(time)
        logger.packet_moved(self, prev, C, time)

    def dropped(self, reason="dropped", time=None):
        if time is not None:
            self.history_time.append(time)
        self.history_time.append(-1)
        self.status = Status.DEAD
        t = time if time is not None else (self.history_time[-2] if len(self.history_time) > 1 and self.history_time[-2] != -1 else 0)
        logger.packet_dropped(self, reason, t)

    def __del__(self):
        self.status = Status.DEAD   # This should never be run
