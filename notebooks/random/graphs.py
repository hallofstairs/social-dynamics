# %% Imports

import random
from typing import Optional

from raphtory import Graph

# %% Erdos-Renyi G(N, p)


def erdos_renyi(
    g: Graph,
    n_nodes: int,
    edge_probability: Optional[float] = None,
    n_edges: Optional[int] = None,
    seed: Optional[int] = None,
) -> Graph:
    """Generates a graph using the Erdos-Renyi model."""

    if seed:
        random.seed(seed)

    latest_time = g.latest_time if g.nodes else 0
    ids = [node.id for node in g.nodes]
    max_id = max(ids) if ids else 0

    # Fill
    for _ in range(n_nodes):
        g.add_node(latest_time, max_id)

    return g


# %%

g = Graph()

erdos_renyi(g, 10, edge_probability=0.5, seed=42)
