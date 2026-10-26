import logging
import heapq
import random
from config import Node, Edge
from packet import Packet

Node_init = 1
Node_end = 100
Packet_init = 10
Packet_end = 1000
Size_init = 10
Size_end = 100    



class Network:
    def __init__(self, nodes = 0, edges = 0):
        
        if nodes == 0:
            nodes = random.randint(Node_init, Node_end)
        if edges == 0:
            edges = random.randint(nodes, nodes*nodes/5)

        self.nodes = nodes
        self.edges = edges
        self.traffic_count = 0
        self.generate_graph(nodes, edges)
        self.packet_count = 0
        self.packet_list = [] 
        self.packet_queue = []


        self.time = 0

    def generate_graph(self):
        self.network = [[-1 for _ in range(self.nodes)] for _ in range(self.nodes)]
        self.traffic = [[-1 for _ in range(self.nodes)] for _ in range(self.nodes)]
        self.node_list = []
        self.edge_list = []
        for _ in range(self.nodes):
            self.node_list.append(Node(_))
        for _ in range(self.edges):
            A = -1
            B = -1
            while A == B:
                A = random.randint(0,self.nodes) 
                B = random.randint(0,self.nodes)
            while A!=B and self.network[A][B] == -1:    # Add a Case for a completely full graph
                self.edge_list.append(Edge(A,B))
                self.network[A][B] = _
                self.network[B][A] = _
                self.node_list[A].add_edge(B, _) #break point
                self.node_list[B].add_edge(A, _) #break point

    def add_edge(self, A = -1, B = -1):
        self.nodes += 1
        while A == B:
            A = random.randint(0, self.nodes)
            B = random.randint(0, self.nodes)
        while A!=B and self.network[A][B] == -1:    # Add a Case for a completely full graph
            self.edge_list.append(Edge(A,B))
            self.network[A][B] = self.nodes
            self.network[B][A] = self.nodes
            self.node_list[A].add_edge(B, self.nodes) #break point
            self.node_list[B].add_edge(A, self.nodes) #break point

    def add_node(self):
        for _ in range(self.nodes):
            self.network[_].append(-1)
            self.traffic[_].append(-1)
        self.nodes += 1
        self.node_list.append(Node(self.nodes-1))
        self.network.append([-1 for _ in range(self.nodes)])
        self.traffic.append([-1 for _ in range(self.nodes)])
        

    def populate_node():
        pass

    def generate_traffic(self, A = -1, B = -1, packets = -1, size = -1, ttl = 50):
        while A == B:
            A = random.randint(0, self.nodes)
            B = random.randint(0, self.nodes)

        if packets <= 0:
            packets = random.randint(Packet_init,Packet_end)

        if self.traffic[A][B] <= 0:
            self.traffic_count += 1

        self.traffic[A][B] += packets
        self.traffic[B][A] += packets

        if size <= 0 :
            size = random.randint(Size_init, Size_end)

        self.packet_list.append(Packet(self.packet_count, A, B, size, self.time, ttl))
        heapq.heappush(self.packet_queue, (self.packet_list[-1].history_time[-1], self.packet_list[-1].id))
        self.packet_count += 1


    def generate_packet(self, A = -1, B = -1, size = -1, ttl = 50):
        while A == B:
            A = random.randint(0, self.nodes)
            B = random.randint(0, self.nodes)

        if size <= 0 :
            size = random.randint(Size_init, Size_end)

        self.packet_list.append(Packet(self.packet_count, A, B, size, self.time, ttl))
        heapq.heappush(self.packet_queue, (self.packet_list[-1].history_time[-1], self.packet_list[-1].id))
        self.packet_count += 1

    def next_packet(self):
        packet = heapq.heappop(self.packet_queue)

        self.time = self.packet_list[packet[1]].history_time[-1]    # Updating Time to the next latest time


        node_id = self.packet_list[packet[1]].history_loc[-1]
        self.node_list[node_id].receive_packet(self.packet_list[packet[1]], self.time)

        if self.packet_list[packet[1]].history_time != -1:          # Avoiding the ones which are lost or have reached their end
            heapq.heappush(self.packet_queue, (self.packet_list[packet[1]].history_time[-1], self.packet_list[packet[1]].id))
        else:   # if it is part of a generated traffic then continue the traffic 
            A = self.packet_list[packet[1]].start_loc
            B = self.packet_list[packet[1]].end_loc
            if self.traffic[B][A] <= 0:
                self.traffic[B][A] -= 1
                self.generate_packet(B, A, self.packet_list[packet[1]].size)
        