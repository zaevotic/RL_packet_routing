import random
import heapq
import logger

from bots import Greedy
'''
Information on Every edge connected to it
Nodes connected to it
Information on packet

'''

PROC_TIME = 5

class Node:
    def __init__(self, id):
        self.id = id    # 0 to n
        self.proc_time = PROC_TIME
        self.neighbours = {}

        self.policy = Greedy(id)

    def add_edge(self, B, edge):
        self.neighbours[B] = edge
        self.policy.add_neighbor(B, edge)

    def receive_packet(self, packet, time):

        history_loc = packet.history_loc

        if packet.end_loc == self.id:
            packet.reached(time)
            # Calculate and return a reward
            return

        temp = 2
        for loc in history_loc:
            if(loc == self.id):
                temp -= 1

        if temp <= 0:
            logger.packet_loop(packet, self.id, time)
            packet.dropped("Routing loop", time)
            # add a penalty for the loop
            return

        # call to the RL
        destination = self.policy.run()
        new_time = self.neighbours[destination].send_packet(packet, time)

        packet.sent(destination, new_time)
        return


        

        
    
'''
speed : bits/s

bandwidth : is the number of simul packets 

capacity : current simul packets being sent
'''

class Edge:
    def __init__(self, A , B, speed = 0, bandwidth = 0):
        self.A = A
        self.B = B

        self.update_speed(speed)
        self.update_bandwidth(bandwidth)

        self.capacity = 0

        self.time_heap = []

    def other_end(self, C):
        if C == self.A:
            return self.B
        else:
            return self.A

    def update_bandwidth(self, bandwidth = 0):
        if bandwidth == 0:
            self.bandwidth = random.randint(1,10) 
            # Updated Bandwidth will start affecting after the capacity decreases

    def update_speed(self, speed = 0):
        if speed == 0:
            self.speed = random.randint(1,10)

    def delete_edge(self):
        if self.capacity == 0:
            self.A = -1
            self.B = -1
            self.speed = -1
            self.bandwidth = -1

    def send_packet(self, packet, time):
        start_time = time
        if(self.capacity >= self.bandwidth):
            start_time = self.time_heap[self.capacity - self.bandwidth]
        self.capacity += 1

        start_time -= (-packet.size // self.speed)
        heapq.heappush(self.time_heap, start_time)

        return start_time
        