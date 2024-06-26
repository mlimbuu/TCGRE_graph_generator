import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class RandomConnection_Graph_Generator:
    def __init__(self, num_vertices):
        self.V = num_vertices  # number of vertices
        self.adjacency_matrix_list = None
        self.G = None

    def create_graph_from_adjacency_matrix(self):
        self.adjacency_matrix_list = self.generate_adjacency_matrix()
        # withou loops
        # self.adjacency_matrix_list = self.generate_adjacency_matrix_without_self_loops()
        self.G = nx.from_numpy_array(np.array(self.adjacency_matrix_list))
        self.G = self.ensure_connected()
        return self.G
    
    
    def generate_adjacency_matrix(self):
        # Set a random seed to ensure reproducibility of the random numbers
        np.random.seed(111)
        # Generate a random binary matrix where each element is either 0 or 1.
        # This matrix is of size VxV and is initially not symmetrical.
        binary_matrix = np.random.randint(0, 2, (self.V, self.V))
        
        # Create a lower triangular matrix from the random matrix. This includes the diagonal.
        lower_triangular = np.tril(binary_matrix)
        
        # Create the symmetric adjacency matrix by adding the lower triangular matrix to its transpose.
        # This ensures the matrix is symmetric, representing an undirected graph.
        adjacency_matrix_symmetric = lower_triangular + np.tril(binary_matrix, -1).T
        
        # Convert the symmetric numpy matrix to a list of lists for easier handling in other functions or systems that might not use numpy.
        adjacency_matrix_list = adjacency_matrix_symmetric.tolist()
        # print("Adjacency matrix:", self.adjacency_matrix_list)
        return adjacency_matrix_list
    
    def generate_adjacency_matrix_without_self_loops(self):
        adjacency_matrix = self.generate_adjacency_matrix()
        # Remove self-loops from the adjacency matrix
        for i in range(self.V):
            adjacency_matrix[i][i] = 0
        return adjacency_matrix
    
    def ensure_connected(self):
        # Check if the graph is connected
        if not nx.is_connected(self.G):
            # Get all connected components
            components = list(nx.connected_components(self.G))
            while len(components) > 1:
                # Connect the first node of one component to the first node of another
                connect_from = components[0].pop()
                connect_to = components[1].pop()
                self.G.add_edge(connect_from, connect_to)
                # Update the components list
                components = list(nx.connected_components(self.G))
        else:
            print("Graph is connected")
        return self.G
    
    def plot_graph(self):
        nx.draw(self.G, with_labels=True, edge_color='gray', node_color='skyblue', node_size=500, font_size=15, font_color='w')
        plt.title("Random Connection Graph")
        # Save the plot
        plt.savefig(f"./random_connection/plots/random_connection_graph_N{self.V}.png")
        # Display the plot
        plt.show()


