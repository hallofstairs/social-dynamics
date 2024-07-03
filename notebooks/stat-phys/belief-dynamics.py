# %% Imports

import json

from pyvis.network import Network
from raphtory import Graph

# %% Generate graph structures

pyvis_options = {
    "edges": {
        "scaling": {
            "min": 1,
            "max": 10,
        },
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

        for i in range(n_nodes):
            for j in range(1, n_neighbors // 2 + 1):
                g.add_edge(0, i, (i + j) % n_nodes)  # Add forward edges
                g.add_edge(0, i, (i - j) % n_nodes)  # Add backward edges

        return g


# %%

ring_lattice_g = Graphs.ring_lattice(n_nodes=10, n_neighbors=2)

ring_lattice_vis: Network = ring_lattice_g.to_pyvis(directed=True, notebook=False)
ring_lattice_vis.set_options(json.dumps(pyvis_options))

ring_lattice_vis.write_html("./graphs/ring-lattice.html")
