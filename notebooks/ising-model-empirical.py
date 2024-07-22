# %% Imports

import raphtory as rp

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
