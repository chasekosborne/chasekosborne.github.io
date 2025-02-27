import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# ----- Parameters -----
N = 500                   # Number of particles per sample
box_size = 1.0            # Size of the 2D square box
A = box_size**2           # Area of the box
density = (N - 1) / A     # Effective density (excluding the reference)

# ----- Radial Bins -----
num_bins = 50
r_max = box_size / 2.0    # Use half the box size
bins = np.linspace(0, r_max, num_bins + 1)
dr = bins[1] - bins[0]
bin_centers = (bins[:-1] + bins[1:]) / 2

# Expected count per sample in each bin (using 2πr dr for small dr)
expected_per_sample = density * (2 * np.pi * bin_centers * dr)

# Data storage for averaging over samples
cumulative_hist = np.zeros(num_bins)
n_samples = 0

# ----- Set Up the Figure and Axes -----
fig, (ax_box, ax_gr) = plt.subplots(1, 2, figsize=(12, 6))

# Left subplot: Simulation Box
ax_box.set_xlim(0, box_size)
ax_box.set_ylim(0, box_size)
ax_box.set_aspect('equal')
ax_box.set_title("Simulation Box (New Sample)")
# Create an initial sample for plotting
initial_positions = np.random.rand(N, 2) * box_size
scat = ax_box.scatter(initial_positions[:, 0], initial_positions[:, 1],
                      s=20, color='blue', alpha=0.5)
# Marker for the reference particle (we'll update its position)
ref_marker, = ax_box.plot([], [], 'ro', markersize=8)

# Right subplot: Evolution of Averaged g(r)
ax_gr.set_xlim(0, r_max)
ax_gr.set_ylim(0, 2)
ax_gr.set_xlabel("r")
ax_gr.set_ylabel("g(r)")
ax_gr.set_title("Evolution of Averaged g(r)")
ax_gr.axhline(1, color='red', linestyle='--', label="g(r)=1")
gr_line, = ax_gr.plot([], [], 'bo-', lw=2, label="Averaged g(r)")
ax_gr.legend()
info_text = ax_gr.text(0.05, 1.8, "", fontsize=12)

# ----- Periodic Distance Function -----
def periodic_distance(u, v, box_size=box_size):
    """Compute the periodic distance between u and v using the minimum image convention."""
    delta = u - v
    delta = delta - box_size * np.round(delta / box_size)
    return np.sqrt(np.sum(delta**2))

# ----- Animation Update Function -----
def update(frame):
    global cumulative_hist, n_samples
    # Generate a new independent sample (configuration) of particles.
    positions = np.random.rand(N, 2) * box_size
    # Update the scatter plot with the new sample.
    scat.set_offsets(positions)
    
    # Choose the reference particle (e.g., the first particle).
    ref = positions[0]
    ref_marker.set_data(ref[0], ref[1])
    
    # Compute distances from the reference to all other particles (using periodic BCs).
    dists = np.array([periodic_distance(ref, pos) for i, pos in enumerate(positions) if i != 0])
    
    # Bin the distances for the current sample.
    hist, _ = np.histogram(dists, bins=bins)
    cumulative_hist += hist
    n_samples += 1
    
    # Compute the average g(r) over all samples so far.
    avg_g = cumulative_hist / (n_samples * expected_per_sample)
    gr_line.set_data(bin_centers, avg_g)
    
    # Update the text with the number of samples used.
    info_text.set_text(f"Samples used: {n_samples}")
    
    return scat, ref_marker, gr_line, info_text

# ----- Create the Animation -----
num_frames = 497  # Number of independent samples to average over
anim = FuncAnimation(fig, update, frames=np.arange(num_frames),
                     interval=1, blit=True, repeat=False)

# ----- (Optional) Save as a GIF -----
# Uncomment the lines below to save the animation as a GIF (requires Pillow).
writer = PillowWriter(fps=100)
anim.save("evolving_gr_new_samples.gif", writer=writer)


plt.tight_layout()
plt.show()