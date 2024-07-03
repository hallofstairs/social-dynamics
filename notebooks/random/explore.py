# %% Imports

from typing import cast

import h5py
import numpy as np
from scipy.sparse import csr_matrix

# %% Create toy bipartite graph

# Create a small bipartite graph
# Set A: 4 nodes (0, 1, 2, 3)
# Set B: 3 nodes (0, 1, 2)
# Edges: (A0-B0), (A0-B2), (A1-B1), (A2-B0), (A2-B2), (A3-B1)

row: np.ndarray = np.array([0, 0, 1, 2, 2, 3])
col: np.ndarray = np.array([0, 2, 1, 0, 2, 1])
data: np.ndarray = np.ones_like(row)
graph = csr_matrix((data, (row, col)), shape=(4, 3))

print("Original graph:")
print(graph.toarray())

# %% Save graph

file = "../data/toy-bipartite.h5"

with h5py.File(file, "w") as f:
    g = f.create_group("bipartite_graph")
    g.create_dataset("data", data=graph.data)
    g.create_dataset("indices", data=graph.indices)
    g.create_dataset("indptr", data=graph.indptr)
    g.create_dataset("shape", data=graph.shape)

# %% Load graph

file = "../data/toy-bipartite.h5"

with h5py.File(file, "r") as f:
    g = cast(h5py.Dataset, f["bipartite_graph"])
    loaded_graph = csr_matrix(
        (g["data"][:], g["indices"][:], g["indptr"][:]), shape=tuple(g["shape"][:])
    )


print("\nLoaded graph:")
print(loaded_graph.toarray())

# %% Analyze graph

# Perform some operations on the graph
print("\nNumber of edges:", loaded_graph.nnz)
print("Degree of nodes in set A:", loaded_graph.sum(axis=1).A1)
print("Degree of nodes in set B:", loaded_graph.sum(axis=0).A1)

# Find nodes with highest degree in each set
max_degree_A = loaded_graph.sum(axis=1).argmax()
max_degree_B = loaded_graph.sum(axis=0).argmax()
print(f"\nNode with highest degree in set A: {max_degree_A}")
print(f"Node with highest degree in set B: {max_degree_B}")

# Check if two nodes are connected
node_A, node_B = 0, 2
is_connected: bool = loaded_graph[node_A, node_B] != 0
print(f"\nAre nodes A{node_A} and B{node_B} connected? {is_connected}")
