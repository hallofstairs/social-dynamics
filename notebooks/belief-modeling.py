# %% Imports

import numpy as np
import numpy.typing as npt

# %% Toy example


w = 0.5
beta = 1

n_beliefs = 2
n_nodes = 3

# Initialize network structure
connections = np.array(
    [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]
)

# TODO: ensure the diagonal is zero (no self-connections)


def kronecker_matrix(n_beliefs: int = 2, n_nodes: int = 3) -> npt.NDArray:
    return np.repeat(np.eye(n_beliefs)[np.newaxis, :, :], n_nodes, axis=0)


# Initialize focal beliefs, internal field, and social field
sigma = np.array([[1, 0], [0, 1], [1, 0]])
h_ind = np.array([[1, 0], [1, 0], [1, 0]])
h_soc = np.array([[0, 1], [1, 0], [0, 1]])  # TODO: Actually calculate

kronecker = kronecker_matrix(n_beliefs, n_nodes)

# TODO: Understand this better
d_ind = np.sum((kronecker - h_ind[:, np.newaxis, :]) ** 2, axis=2)
d_soc = np.sum((kronecker - h_soc[:, np.newaxis, :]) ** 2, axis=2)

h = (1 - w) * d_ind + w * d_soc

# Calculate Boltzmann factors and probabilities using softmax
boltzmann_factors = np.exp(-beta * h)
partition_functions = np.sum(boltzmann_factors, axis=1)
sigma = boltzmann_factors / partition_functions[:, np.newaxis]
