import random


'''
Information on Every edge connected to it
Nodes connected to it
Information on packet

'''
class Node:
    def __init__(self, id):
        self.id = id    # 0 to n
        self.neighbours = {}

    def add_edge(self, B, edge_id):
        self.neighbours[B] = edge_id

    def receive_packet(self, packet):

        # call to the RL

        pass
    
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

    def update_bandwidth(self, bandwidth = 0):
        if bandwidth == 0:
            self.bandwidth = random.randint(1,10) 
            # Updated Bandwidth will start affecting after the capacity decreases

    def update_speed(self, speed = 0):
        if speed == 0:
            self.bandwidth = random.randint(1,10)

    def delete_edge(self):
        if self.capacity == 0:
            self.A = -1
            self.B = -1
            self.speed = -1
            self.bandwidth = -1

    def send_packet(self, packet_id):
        if(self.capacity >= self.bandwidth):
            pass
            # Return an Error
        self.capacity += 1

        

    
