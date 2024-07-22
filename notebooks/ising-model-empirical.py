# %% Imports

import json
import os
import random
import typing as t

import raphtory as rp

STREAM_DIR = "../data/stream"

# %%


g = rp.Graph()


def init_belief():
    return random.choice([-1, 1])


def update_belief(n: rp.Node, p: rp.Properties):
    p.as_dict()

    return


for day in sorted(os.listdir(STREAM_DIR)):
    # Insert new information into graph
    with open(f"{STREAM_DIR}/{day}", "r") as file:
        for line in file:
            record = json.loads(line.strip())

            # Insert new nodes
            if record["$type"] == "app.bsky.actor.profile":
                g.add_node(
                    timestamp=record["createdAt"],
                    id=record["did"],
                    properties={"belief": init_belief()},
                )

            # Draw new edges
            elif record["$type"] == "app.bsky.graph.follow":
                g.add_edge(
                    timestamp=record["createdAt"],
                    src=record["did"],
                    dst=record["subject"],
                )

    # Update nodes
    for node in t.cast(list[rp.Node], g.nodes):
        # Get a random sample of
        node.properties

        # Chinatown soup: tea tasting

    break


# %%


# %%


# For every time t (daily):
#   New data introduced:
#       - New nodes (users)
#           - Insert new nodes into network, initialize beliefs of nodes
#       - New edges (follows)
#           -
#       - New posts (posts)
#       - New interactions (likes, reposts, quotes, replies)
#   Processes:
#       - Belief updating
#           - Who should be updated? Everyone who was "consumer-active"? (Did at least one action)
#           - Instead of selecting a random sample of a node's contacts, select
#             the connections that have been "producer-active" during that period, posting-wise
#           - Use the Hamiltonian to model the evolution of the belief distribution (Potts model?)
#           - Each "consumer-active" individual determines their dissonance according to the
#             Hamiltonian H_i
#
#       - Init their internal and social fields
#   Rules:
#       - Social interaction
#           - How do individuals do social learning? Voter, majority, expert/best-friend rules, etc.
#       - Weight on social interaction
#           - How do individuals weigh social interactions for updating their beliefs?
#   Process posts
#
#   Research questions:
#       - How do people in a social network do social learning? How can we know?
#
