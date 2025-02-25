import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Set random seed for reproducibility
np.random.seed(42)

# Simulation parameters
N = 100         # number of particles
density = 0.8   # number density (particles per unit area)
L = np.sqrt(N / density)   # box length for a square simulation box (2D)
epsilon = 1.0   # LJ energy parameter
sigma = 1.0     # LJ distance parameter
beta = 1.0      # inverse temperature (1/kT)
r_cut = 2.5 * sigma   # cutoff radius

# Define the Lennard-Jones potential with cutoff and shift
def lj_potential(r):
    if r < r_cut:
        U = 4 * epsilon * ((sigma / r)**12 - (sigma / r)**6)
        # Shift the potential so that U(r_cut) = 0
        U_cut = 4 * epsilon * ((sigma / r_cut)**12 - (sigma / r_cut)**6)
        return U - U_cut
    else:
        return 0.0

# Minimum image convention for periodic boundary conditions
def minimum_image(r, L):
    return r - L * np.rint(r / L)

# Monte Carlo simulation parameters
n_steps = 10000   # number of equilibration steps
delta = 0.1       # maximum displacement for trial moves

# Initialize particle positions uniformly in the box
positions = np.random.uniform(0, L, (N, 2))

# Equilibration phase: simple Metropolis moves with progress bar
for step in tqdm(range(n_steps), desc="Equilibrating"):
    i = np.random.randint(0, N)  # choose a random particle
    old_pos = positions[i].copy()
    
    # Propose a move
    move = np.random.uniform(-delta, delta, 2)
    positions[i] += move
    # Apply periodic boundary conditions
    positions[i] %= L
    
    # Compute energy change ΔE (only interactions involving particle i)
    dE = 0.0
    for j in range(N):
        if j != i:
            disp_old = old_pos - positions[j]
            disp_old = minimum_image(disp_old, L)
            r_old = np.linalg.norm(disp_old)
            
            disp_new = positions[i] - positions[j]
            disp_new = minimum_image(disp_new, L)
            r_new = np.linalg.norm(disp_new)
            
            dE += lj_potential(r_new) - lj_potential(r_old)
    
    # Accept or reject the move using the Metropolis criterion
    if dE > 0 and np.random.rand() >= np.exp(-beta * dE):
        positions[i] = old_pos  # reject move

# Now sample configurations to compute the pair correlation function g(r)
n_sample = 5000  # number of samples
dr = 0.05        # bin width for histogram
r_bins = np.arange(0, L/2, dr)
g_hist = np.zeros(len(r_bins) - 1)
n_configs = 0

# Sampling loop with progress bar
for sample in tqdm(range(n_sample), desc="Sampling Configurations"):
    # Do a few MC steps between samples to decorrelate configurations
    for step in range(10):
        i = np.random.randint(0, N)
        old_pos = positions[i].copy()
        move = np.random.uniform(-delta, delta, 2)
        positions[i] += move
        positions[i] %= L
        dE = 0.0
        for j in range(N):
            if j != i:
                disp_old = old_pos - positions[j]
                disp_old = minimum_image(disp_old, L)
                r_old = np.linalg.norm(disp_old)
                
                disp_new = positions[i] - positions[j]
                disp_new = minimum_image(disp_new, L)
                r_new = np.linalg.norm(disp_new)
                
                dE += lj_potential(r_new) - lj_potential(r_old)
        if dE > 0 and np.random.rand() >= np.exp(-beta * dE):
            positions[i] = old_pos  # reject move
            
    # Sample the current configuration: compute all pair distances
    for i in range(N - 1):
        for j in range(i + 1, N):
            disp = positions[i] - positions[j]
            disp = minimum_image(disp, L)
            r = np.linalg.norm(disp)
            if r < L/2:
                bin_index = int(r / dr)
                # Ensure the bin index is within bounds
                if bin_index < len(g_hist):
                    g_hist[bin_index] += 2  # count each pair (i,j) and (j,i)
    n_configs += 1

# Normalize the histogram to obtain g(r)
g_sim = np.zeros_like(g_hist)
area = L**2
rho = N / area
for i in range(len(g_hist)):
    r_lower = i * dr
    r_upper = (i + 1) * dr
    shell_area = np.pi * (r_upper**2 - r_lower**2)
    ideal_pairs = shell_area * rho
    # Normalization by number of particles and number of configurations
    g_sim[i] = g_hist[i] / (n_configs * N * ideal_pairs)

# Compute the theoretical g(r) for the low-density approximation
r_values = np.linspace(0.9 * sigma, L/2, 200)  # avoid r = 0 singularity
g_theory = np.array([np.exp(-beta * lj_potential(r)) for r in r_values])

# Plot both the simulation and theoretical results
plt.figure(figsize=(8, 6))
r_centers = (np.arange(len(g_sim)) + 0.5) * dr  # bin centers for simulation data

plt.plot(r_centers, g_sim, label='Simulation g(r)', marker='o', linestyle='-', markersize=4)
plt.plot(r_values, g_theory, label='Theoretical g(r) [low-density]', linestyle='--')

plt.xlabel('r')
plt.ylabel('g(r)')
plt.title('Lennard-Jones Fluid: Simulation vs. Theoretical Pair Correlation Function')
plt.legend()
plt.grid(True)

# Save the plot as an SVG file
plt.savefig("lennard_jones_g_r.svg", format="svg")
plt.show()
