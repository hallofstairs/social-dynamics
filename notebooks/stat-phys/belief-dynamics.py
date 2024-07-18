# %% Imports

import json
import random

import numpy as np
from pyvis.network import Network
from raphtory import Graph

# %% Generate graph structures

pyvis_options = {
    "height": "1000px",
    "width": "100%",
    "edges": {
        "scaling": {
            "min": 1,
            "max": 10,
        },
    },
    "layout": {
        "randomSeed": 42,
        "improvedLayout": True,
    },
    "physics": {
        "barnesHut": {
            "gravitationalConstant": -30000,
            "centralGravity": 0.3,
            "springLength": 100,
            "springConstant": 0.05,
        },
        "maxVelocity": 50,
        "timestep": 0.5,
    },
}


class Graphs:
    @staticmethod
    def ring_lattice(n_nodes: int, n_neighbors: int) -> Graph:
        if n_neighbors % 2 != 0:
            raise ValueError("n_neighbors must be even")
        if n_neighbors >= n_nodes:
            raise ValueError("n_neighbors must be less than n_nodes")

        g = Graph()

        # Populate the graph with n_nodes nodes
        for i in range(n_nodes):
            g.add_node(0, i)

        # Create lattice
        for i in range(n_nodes):
            for j in range(1, n_neighbors // 2 + 1):
                g.add_edge(0, i, (i + j) % n_nodes)

        return g

    @staticmethod
    def small_world_lattice(  # aka Watts-Strogatz model
        n_nodes: int, n_neighbors: int, p_rewire: float
    ) -> Graph:
        if n_neighbors % 2 != 0:
            raise ValueError("n_neighbors must be even")
        if n_neighbors >= n_nodes:
            raise ValueError("n_neighbors must be less than n_nodes")

        g = Graph()

        # Populate the graph with n_nodes nodes
        for i in range(n_nodes):
            g.add_node(0, i)

        # Create initial lattice, with rewiring
        for i in range(n_nodes):
            for j in range(1, n_neighbors // 2 + 1):
                if random.random() < p_rewire:
                    valid_shortcuts = [
                        idx
                        for idx in range(n_nodes)
                        if not g.has_edge(i, idx) and i != idx
                    ]

                    g.add_edge(0, i, random.sample(valid_shortcuts, 1)[0])
                else:
                    g.add_edge(0, i, (i + j) % n_nodes)

        return g

    @staticmethod
    def fully_connected(n_nodes: int) -> Graph:
        g = Graph()

        # Populate the graph with n_nodes nodes
        for i in range(n_nodes):
            g.add_node(0, i)

        # Create fully connected network
        for i in range(n_nodes):
            for j in range(i):
                g.add_edge(0, i, j)

        return g

    @staticmethod
    def stochastic_block(n_nodes: int, k_blocks: int) -> Graph:
        g = Graph()

        # Populate the graph with n_nodes nodes, assign each node to a block
        for i in range(n_nodes):
            block_assignment = random.randint(0, k_blocks - 1)
            g.add_node(
                0,
                i,
                node_type=str(block_assignment),
                properties={"block": block_assignment},
            )

        # Create K-K matrix with block affinities
        k_mat: np.ndarray = np.tri(k_blocks, k=-1, dtype=float)

        for i in range(k_blocks):
            for j in range(i + 1):
                k_mat[i, j] = random.random()

        # k_mat.fill() += k_mat.T

        print(k_mat)

        # Create edges based on K-K matrix

        return g


# %% Ring lattice

ring_lattice_g = Graphs.ring_lattice(n_nodes=40, n_neighbors=10)

ring_lattice_vis: Network = ring_lattice_g.to_pyvis(directed=False, notebook=False)
ring_lattice_vis.set_options(json.dumps(pyvis_options))

ring_lattice_vis.write_html("./graphs/ring-lattice.html")

# %% Small-world lattice

small_world_lattice_g = Graphs.small_world_lattice(
    n_nodes=20, n_neighbors=6, p_rewire=0.05
)

small_world_lattice_vis: Network = small_world_lattice_g.to_pyvis(
    directed=False, notebook=False
)
small_world_lattice_vis.set_options(json.dumps(pyvis_options))

small_world_lattice_vis.write_html("./graphs/small-world-lattice.html")


# %% Fully-connected network

fully_connected_graph = Graphs.fully_connected(10)

fully_connected_vis: Network = fully_connected_graph.to_pyvis(
    directed=False, notebook=False
)
fully_connected_vis.set_options(json.dumps(pyvis_options))

fully_connected_vis.write_html("./graphs/fully-connected.html")

# %% Stochastic block network

stochastic_block_network = Graphs.stochastic_block(10, 4)

stochastic_block_vis: Network = stochastic_block_network.to_pyvis(
    directed=False, notebook=False, colour_nodes_by_type=True
)
stochastic_block_vis.set_options(json.dumps(pyvis_options))

stochastic_block_vis.write_html("./graphs/stochastic-block.html")
