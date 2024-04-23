import networkx as nx
import random
import time
from er_rg_probability import ErdosRenyi_GNP_Graph_Generator

class TCGRE_ErdosRenyi_GNP_Graph_Generator:

    def __init__(self, n, p, risk_edge_ratio):
        self.n = n
        self.p = p
        
        self.risk_edge_ratio = risk_edge_ratio # risk edges to total edges ratio
        self.risk_edges_with_support_nodes = None # Risk edges with support nodes

        self.source = 0 # default start node
        self.target = n-1 # default target node

        self.TCGRE_G = None # TCGRE Erdos Renyi Graph

    # Create tcgre random graph using the G(n, p) model
    def create_tcgre_gnp_random_graph(self):
        G = ErdosRenyi_GNP_Graph_Generator(self.n, self.p)
        self.TCGRE_G = G.create_gnp_random_graph()
        print("Erdos Renyi Graph created...")
        return self.TCGRE_G
    
    # pick edges on the shortest path for additional risk edges
    def pick_edges_on_shortest_path(self):
        print(f"Source: {self.source}, Target: {self.target}")
        # Find all shortest paths between source and target
        all_shoretest_paths = list(nx.all_shortest_paths(self.TCGRE_G, source=self.source, target=self.target, weight='weight'))
        print(f"all_shoretes_paths: {all_shoretest_paths}")
    
        # Unique edges from all shortest paths
        unique_edges = set()
        for path in all_shoretest_paths:
            # Extract edges from the path (consecutive pairs of nodes) and add them to the set
            edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            unique_edges.update(edges)    

        return all_shoretest_paths, list(unique_edges)
    
    # pick neighbors of the risk edges as support nodes
    def pick_support_nodes(self, risk_edges):
        risk_edge_with_support_nodes = {}
        support_nodes_used = set() 
        ## in many cases same nodes can be used as support nodes for multiple risk edges
        ## and same risk edge can have multiple support nodes
        for edge in risk_edges:
            total_neighbors =  list(self.TCGRE_G.neighbors(edge[0])) +  list(self.TCGRE_G.neighbors(edge[1]))
            
            # special case: only pick one neighbor per risk edge that are not used as support nodes before
            for neighbor in total_neighbors:
                if neighbor in support_nodes_used:
                    total_neighbors.remove(neighbor)
            random_support_node = random.choice(total_neighbors)
            risk_edge_with_support_nodes[edge] = (random_support_node,)

            # update the support nodes used
            support_nodes_used.add(random_support_node)
            print(f"risk_edge_with_support_nodes: {risk_edge_with_support_nodes}")
        return risk_edge_with_support_nodes

    # pick the risk edges and support nodes
    def pick_risk_edges_and_support_nodes(self):
        print("Picking risk edges and support nodes...")
        #Pick radome edges as risk edges from edges, it should be 0.2 of the total edges
        # Calculate the number of edges to select as risky
        num_risk_edges = int(len(self.TCGRE_G.edges()) * self.risk_edge_ratio)

        # Randomly select edges without replacement
        ## one way: add at least some risk edges on the shortest path with other edges
        _, unique_edges_on_shortest_path = self.pick_edges_on_shortest_path()
        risk_edges = random.sample(self.TCGRE_G.edges(), num_risk_edges-1)
        # Filter out edges that are already in risk_edges
        available_edges = [edge for edge in unique_edges_on_shortest_path if edge not in risk_edges]
        ## add the edge on the shortest path
        # Check if there are any available edges to add
        if available_edges:
            # Randomly select an edge that's not already a risk edge
            chosen_edge = random.choice(available_edges)
            print(f"chosen_edge: {chosen_edge}")
            # Add this edge to risk_edges
            risk_edges.append(chosen_edge)

        ## pick up neighbors of the risk edges as support nodes
        self.risk_edges_with_support_nodes = self.pick_support_nodes(risk_edges)
        return self.risk_edges_with_support_nodes

    #  add cost to the edges including the risk edges
    def add_cost_to_edges(self):
        print("Adding cost to the edges...")
        for edge in self.TCGRE_G.edges():
            if edge in self.risk_edges_with_support_nodes.keys():
                print(f"risk_edge: {edge}, support_nodes: {self.risk_edges_with_support_nodes[edge][0]}")
                self.TCGRE_G[edge[0]][edge[1]]['cost'] = [20, (self.risk_edges_with_support_nodes[edge][0],)]
            else:
                print(f"normal_edge: {edge}")
                # either fixed cost for normal edges, lesser than the risk edge cost
                # self.TCGRE_G[edge[0]][edge[1]]['cost'] = 5

                # or random cost for normal edges, between 1 and 10, lesser than the risk edge cost
                self.TCGRE_G[edge[0]][edge[1]]['cost'] = random.randint(1, 10)

        return self.TCGRE_G

    # convert the graph to compatible graph
    def convert_to_compatible_graph(self):
        print("Converting to compatible graph...")
        nodes = {node: {} for node in self.TCGRE_G.nodes()}
        for edge in self.TCGRE_G.edges():
            # Unpack the edge nodes
            node1, node2 = edge
            nodes[node1][node2] = self.TCGRE_G[node1][node2]['cost']  # For node1 -> node2
            nodes[node2][node1] =  self.TCGRE_G[node1][node2]['cost'] # For node2 -> node1
        return nodes
    

# # Parameters
n = 10  # number of nodes
p = 0.5  # probability of an edge # 0.5 default answer
risk_edge_ratio = 0.2 # 20% of the total edges

# # Create a random graph using the G(n, p) model
tcgre_er_p = TCGRE_ErdosRenyi_GNP_Graph_Generator(n, p, risk_edge_ratio)
tcgre_er_p.create_tcgre_gnp_random_graph()
tcgre_er_p.pick_risk_edges_and_support_nodes()
tcgre_er_p.add_cost_to_edges()
graph_info_tcgre_er_p = tcgre_er_p.convert_to_compatible_graph()
print(f"Graph Info: {graph_info_tcgre_er_p}")