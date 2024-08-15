# %% Imports

import json
import time
import typing as t
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import raphtory as rp
import raphtory.algorithms as alg

import graph_tool.all as gt

STREAM_DIR = "../data/stream-2023-07-01"

# %% Functions


def generate_timestamps(until: str) -> list[str]:
    start_date = datetime.strptime("2022-11-17", "%Y-%m-%d")
    end_date = datetime.strptime(until, "%Y-%m-%d")
    delta = end_date - start_date

    return [
        (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(delta.days + 1)
    ]


# %% Efficiency testing

timestamps = generate_timestamps(until="2023-03-10")

g = rp.Graph()

start_time = time.time()
count = 0
for ts in timestamps:
    with open(f"{STREAM_DIR}/{ts}.jsonl", "r") as file:
        for line in file:
            try:
                record = json.loads(line.strip())
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in file {STREAM_DIR}/{ts}: {e}")
                continue

            if record["$type"] == "app.bsky.actor.profile":
                g.add_node(record["createdAt"], record["did"])
            elif record["$type"] == "app.bsky.graph.follow":
                g.add_edge(record["createdAt"], record["did"], record["subject"])
            count += 1

print(
    f"Processed {count} records in {time.time() - start_time:.2f} seconds ({count / (time.time() - start_time):.2f} recs/sec)"
)


# %% Components

if t.cast(rp.Graph, g.largest_connected_component()).count_nodes() == g.count_nodes():
    print("The graph is fully connected.")
else:
    print(
        "The graph is not fully connected. Largest component covers",
        t.cast(rp.Graph, g.largest_connected_component()).count_nodes()
        / g.count_nodes(),
        "% of the graph",
    )


# %% Metrics

sub_g = t.cast(rp.Graph, g.largest_connected_component())

# TODO: Sample nodes for efficiency

# Average clustering coefficient
start = time.time()
avg_clustering_coeff = (
    sum(alg.local_clustering_coefficient(sub_g, node) for node in sub_g.nodes)
    / sub_g.count_nodes()
)
print(f"Avg clustering coeff calc: {time.time() - start:.2f}s")

# Average path length
start = time.time()
path_length = [alg.single_source_shortest_path(sub_g, node) for node in sub_g.nodes]
print(f"Avg path length calc: {time.time() - start:.2f}s")


# Assortativity

# %% With networkx

n_g = sub_g.to_networkx(
    include_edge_properties=False,
    include_node_properties=False,
    include_update_history=False,
    include_property_history=False,
)
n_g = nx.Graph(n_g)

# Average clustering coefficient
start = time.time()
avg_clustering_coeff = nx.average_clustering(n_g)
print(f"Avg clustering coeff calc: {time.time() - start:.2f}s")

# Average path length
start = time.time()
avg_path_length = [nx.shortest_path_length(n_g, node) for node in n_g.nodes]
print(f"Avg path length calc: {time.time() - start:.2f}s")


# %% Graph tool stuff

did_ptrs = {}

g = gt.Graph()

v1 = g.add_vertex()


# %% Populate graph

timestamps = generate_timestamps(until="2023-03-10")

g = gt.Graph()
did_ptrs = {}

start_time = time.time()
count = 0
for ts in timestamps:
    with open(f"{STREAM_DIR}/{ts}.jsonl", "r") as file:
        records = [json.loads(line.strip()) for line in file]

    records.sort(key=lambda x: x.get("createdAt", ""))

    for record in records:
        if record["$type"] == "app.bsky.actor.profile":
            did_ptrs[record["did"]] = g.add_vertex()
        elif record["$type"] == "app.bsky.graph.follow":
            if record["did"] in did_ptrs and record["subject"] in did_ptrs:
                g.add_edge(did_ptrs[record["did"]], did_ptrs[record["subject"]])
        count += 1

print(
    f"Processed {count} records in {time.time() - start_time:.2f} seconds ({count / (time.time() - start_time):.2f} recs/sec)"
)

# %%

# Get the largest connected component
start = time.time()
comps = gt.label_components(g)
sub_g = gt.GraphView(g, vfilt=comps[0].a == np.argmax(comps[1]))
print(f"Graph-tool: Largest component extraction: {time.time() - start:.2f}s")

# %%

# Average clustering coefficient
start = time.time()
local_clustering: gt.VertexPropertyMap = gt.local_clustering(sub_g)
avg_clustering = sum(local_clustering.a) / len(local_clustering.a)
print(f"Graph-tool: Avg clustering coeff calc: {time.time() - start:.2f}s")

# Average path length
start = time.time()
dist = gt.shortest_distance(sub_g)
ave_path_length = sum([sum(i) for i in dist]) / (
    sub_g.num_vertices() ** 2 - sub_g.num_vertices()
)
print(f"Graph-tool: Avg path length calc: {time.time() - start:.2f}s")

# %% Other metrics

# Assortativity
assortativity = gt.assortativity(sub_g, "total")

# Density

V = sub_g.num_vertices()
E = sub_g.num_edges()

if sub_g.is_directed():
    max_edges = V * (V - 1)
else:
    max_edges = V * (V - 1) / 2

density = E / max_edges
