# %% Imports

import typing as t

import numpy as np
import numpy.typing as npt
from scipy.io import loadmat

# %% Load data


def load_mat(file: str, var: str) -> npt.NDArray:
    return t.cast(np.ndarray, loadmat(file).get(var))


def load_nested_mat(file: str, var: str) -> npt.NDArray:
    mat = load_mat(file, var)[0]
    return np.array([row.flatten() for row in mat]).T


# Population data from Ohio (from survey)
pop_survey_se = load_mat("../../data/matlab/pop_survey_se.mat", "pop_survey_se")
pop_survey_mean = load_mat("../../data/matlab/pop_survey_mean.mat", "pop_survey_mean")

# Initial characteristics of simulated voters

# Prob. of voting in 2016 -- 5 cols, each col is a different belief (R, D, O, non voting), sum to 100
s_vote_2016_p = load_nested_mat("../../data/matlab/s_vote2016_p.mat", "s_vote2016_p")

# Demographics of simulated voters
s_age = load_mat("../../data/matlab/s_age.mat", "s_age")  # Age
s_race = load_mat("../../data/matlab/s_race.mat", "s_race")  # Race
s_education = load_mat("../../data/matlab/s_education.mat", "s_education")  # Education
s_hhincome = load_mat("../../data/matlab/s_hhincome.mat", "s_hhincome")  # HH income

# Initial own and social probs of beliefs -- 5 cols, each col is a different belief, sum to 100
# TODO: What do these mean?
s_own_p = load_nested_mat("../../data/matlab/s_own_p.mat", "s_own_p")
s_soc_p = load_nested_mat("../../data/matlab/s_soc_p.mat", "s_soc_p")


# %% Parameters

tmax = 77  # Number of timesteps; days until the election
n = 1000  # Number of simulated voters
k = 10  # Size of voters' social circles
on = 4  # Number of beliefs (R, D, O, non voting)
o_prob = np.array(  # Complete support for each belief
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
)
repmax = 10  # Number of replications with different network structures


# %% Simulation

xhom = 0  # 0 Low homophily, 1 more pronounced homophily
xsocag = 0  # Belief integration rule (0=average, 1=majority)
xevents = 1  # Take into account current events
w = 0.3  # Importance of social dissonance
beta = 1  # Attentiveness to belief updating

# %% Approximate the network structure

# Stack different voter characteristics side by side
values = np.column_stack(
    (s_vote_2016_p[:, 0], s_vote_2016_p[:, 3], s_age, s_race, s_hhincome, s_education)
)

# Normalize each voter characteristic column with Z-score
values = (values - np.nanmean(values, axis=0)) / np.sqrt(np.nanvar(values, axis=0))

difs = np.zeros((n, n))  # Distance between each pair of voters
sims = np.zeros((n, n))  # Similarity between each pair of voters

# Calculate absolute difference between each voter and each other voter
for i in range(n):
    difs[i, :] = np.mean(np.abs(values - values[i]), axis=1)
    sims[i, :] = 1 / difs[i, :]

# Square differences to emphasize larger similarities and devalue smaller
if xhom == 1:
    sims = sims**2

sims[sims == np.inf] = 0  # Similarity to self set to 0 so that self is not chosen

# Calculate the number of connections each voter should have in each category based on their reported social circle's beliefs
remcon = np.zeros((4, n), dtype=int)

remcon[0] = np.round(k * s_soc_p[:, 0] / 100).astype(int)  # R
remcon[1] = np.round(k * s_soc_p[:, 1] / 100).astype(int)  # D
remcon[2] = np.round(k * s_soc_p[:, 2] / 100).astype(int)  # O
remcon[3] = np.round(k - np.sum([remcon[0], remcon[1], remcon[2]], axis=0)).astype(
    int
)  # Non voting

while True:
    conn = np.zeros((n, n))  # Create connection matrix

    # For each voter
    for voter_idx in range(n):
        # For each category of belief
        for g in range(on):
            pop = np.arange(n)  # Population to choose contacts from

            # Filter population to only include voters who have same belief as the voter and have capacity
            pop = pop[(s_own_p[:, g] != 0) & (remcon[g] != 0)]

            # Voter's similarities to every contact that made it through the filter
            sims_pop = sims[voter_idx, pop]

            # If there are enough potential contacts and the voter has capacity
            if len(pop) > remcon[g][voter_idx] and remcon[g][voter_idx] > 0:
                # Randomly select contacts
                temp = np.random.choice(
                    pop,
                    size=remcon[g][voter_idx],
                    replace=True,
                    p=sims_pop / np.sum(sims_pop),
                )

                temp = np.unique(temp)  # Remove repetitions
                conn[voter_idx, temp] = 1
                conn[temp, voter_idx] = 1  # connections established
                remcon[g][voter_idx] -= len(temp)  # i loses capacity for j-type others
                for jj in range(4):  # others lose capacity for whatever type i is
                    if s_own_p[:, jj][voter_idx] == 1:  # if i was j kind of person
                        remcon[jj][temp] -= 1

    # Check if every voter has at least one connection
    a = np.sum(conn, axis=1)

    # If network is fully connected, return
    if np.sum(a == 0) == 0:
        break

# Calculate the sum of each row in the connection matrix
row_sums = np.sum(conn, axis=1)

# %% Save data

# Save the connection matrix as a text file with pairs
# with open("../../data/polling/net-structure.txt", "w") as f:
#     for i in range(n):
#         for j in range(i + 1, n):  # Start from i+1 to avoid duplicates
#             if conn[i, j] == 1:
#                 f.write(f"{i},{j}\n")

np.savetxt("../../data/polling/net-structure.txt", conn)
# Datasets
#   - Structure updates ()
#   - Events (when do users change their beliefs)
#   - Voter characteristics
#   - Actual beliefs


# %% Process network matrix for belief modeling

ts = 0  # timestep zero

# Store individual and social fields over time
s_cog = []  # Internal field
s_own_pred = []  # Focal beliefs
s_soc = []  # Social field

# Initialize internal fields
s_cog.append(s_vote_2016_p[:, :4] / 100)  # Copy from s_vote_2016_p, make sum to 1

# Initialize focal beliefs
s_own_pred.append(s_own_p[:, :4] / 100)  # Copy from s_own_p, make sum to 1

# Make initial individual field a bit less extreme and replace zeros with 0.1
s_cog[ts] = s_cog[ts] * 0.7
s_cog[ts][s_cog[ts] == 0] = 0.1

# Initialize social fields -- average focal belief of each voter's social circle
s_soc_init = []

for voter_idx, connections in enumerate(conn):
    soc_fields = []

    for contact_idx, is_connected in enumerate(connections):
        if is_connected:
            soc_fields.append(s_own_p[contact_idx][:4])

    s_soc_init.append(np.mean(np.array(soc_fields), axis=0))

s_soc.append(s_soc_init)

# Initialize average/std focal beliefs (t=0)
s_percs_mean = np.mean(s_own_pred[ts][:, 0], axis=0)
s_percs_std = np.std(s_own_pred[ts][:, 0], axis=0)


# %% Implement belief dynamics

for ts in range(1, tmax):
    diss_ind = np.zeros((n, on))
    diss_soc = np.zeros((n, on))

    # Calcuate dissonance for each belief, individual
    for belief in range(on):  # For each possible focal belief
        diss_ind = (np.tile(o_prob[belief], (n, 1)) - s_cog[ts - 1]) ** 2

        diss_soc = 0

        diss_tot = (1 - w) * diss_ind + w * diss_soc
