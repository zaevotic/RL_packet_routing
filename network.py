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

    def generate_graph(self):
        self.network = [[-1 for _ in range(self.nodes)] for _ in range(self.nodes)]
        self.traffic = [[-1 for _ in range(self.nodes)] for _ in range(self.nodes)]
        self.node_list = []
        self.edge_list = []
        for _ in range(self.nodes):
            self.node_list.append(Node(_))
        for _ in range(self.edges):
            A = random.randint(0,self.nodes) 
            B = random.randint(0,self.nodes)
            while A!=B and self.network[A][B] == -1:
                self.edge_list.append(Edge(A,B))
                self.network[A][B] = _
                self.network[B][A] = _
                self.node_list[A].add_edge(B, _) #break point
                self.node_list[B].add_edge(A, _) #break point

    def add_edge(self, A = -1, B = -1):
        self.nodes += 1
        if A == B:
            A = random.randint(0, self.nodes)
            B = random.randint(0, self.nodes)
        while A!=B and self.network[A][B] == -1:
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

    def generate_traffic(self, A = -1, B = -1, packets = -1):
        while A == B:
            A = random.randint(0, self.nodes)
            B = random.randint(0, self.nodes)

        if packets <= 0:
            packets = random.randint(Packet_init,Packet_end)

        if self.traffic[A][B] <= 0:
            self.traffic_count += 1

        self.traffic[A][B] += packets
        self.traffic[B][A] += packets

    def generate_packet(self, A = -1, B = -1, size = -1, ttl = 50):
        if A == B:
            A = random.randint(0, self.nodes)
            B = random.randint(0, self.nodes)

        if size <= 0 :
            size = random.randint(Size_init, Size_end)

        self.packet_list.append(Packet(self.packet_count, A, B, size, ttl))
        self.packet_count += 1

        