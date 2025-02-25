import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# ----- Parameters -----
N = 500                   # Total number of particles
box_size = 1.0            # Size of the 2D square box
A = box_size**2           # Area of the box
density = (N - 1) / A     # Effective density for each reference (excluding itself)

# ----- Generate Ideal Gas Configuration -----
positions = np.random.rand(N, 2) * box_size

# ----- Set Up Radial Bins -----
num_bins = 50
r_max = box_size / 2.0    # Maximum r (using half the box size)
bins = np.linspace(0, r_max, num_bins + 1)
dr = bins[1] - bins[0]
bin_centers = (bins[:-1] + bins[1:]) / 2

# For each reference particle, the expected number in the annulus is:
# expected = density * (area of annulus)
# Here we approximate the annulus area as: 2πr dr (which is good for small dr)
expected_per_reference = density * (2 * np.pi * bin_centers * dr)

# ----- Prepare Data Storage for Averaging -----
cumulative_hist = np.zeros(num_bins)  # Cumulative histogram over reference particles
n_refs_used = 0                      # Number of reference particles processed so far

# ----- Create Figure and Axes for Animation -----
fig, (ax_box, ax_gr) = plt.subplots(1, 2, figsize=(12, 6))

# Left: Simulation Box
ax_box.set_xlim(0, box_size)
ax_box.set_ylim(0, box_size)
ax_box.set_aspect('equal')
ax_box.set_title("Simulation Box (Reference Particle Highlighted)")
scat = ax_box.scatter(positions[:, 0], positions[:, 1],
                      s=20, color='blue', alpha=0.5)
ref_marker, = ax_box.plot([], [], 'ro', markersize=8)

# Right: g(r) Plot
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
    """Compute the distance between points u and v in a periodic box."""
    delta = u - v
    # Apply the minimum image convention
    delta = delta - box_size * np.round(delta / box_size)
    return np.sqrt(np.sum(delta**2))

# ----- Animation Update Function -----
def update(frame):
    global cumulative_hist, n_refs_used
    # Use the frame number as the index for the reference particle.
    # (For simplicity, we cycle through the particles.)
    ref_idx = frame % N
    ref = positions[ref_idx]
    ref_marker.set_data(ref[0], ref[1])
    
    # Compute distances from this reference to all other particles using periodic BCs.
    dists = []
    for i in range(N):
        if i == ref_idx:
            continue
        d = periodic_distance(ref, positions[i])
        dists.append(d)
    dists = np.array(dists)
    
    # Bin these distances for the current reference.
    hist, _ = np.histogram(dists, bins=bins)
    cumulative_hist += hist
    n_refs_used += 1
    
    # Compute the average g(r) over all processed reference particles.
    # For each bin, the expected count per reference is "expected_per_reference",
    # so for n_refs_used references, expected_total = n_refs_used * expected_per_reference.
    avg_g = cumulative_hist / (n_refs_used * expected_per_reference)
    
    # Update the g(r) plot.
    gr_line.set_data(bin_centers, avg_g)
    info_text.set_text(f"References used: {n_refs_used}")
    return scat, ref_marker, gr_line, info_text

# ----- Create the Animation -----
num_frames = 497  # Number of reference particles to average over
anim = FuncAnimation(fig, update, frames=np.arange(num_frames),
                     interval=1, blit=True, repeat=False)

writer = PillowWriter(fps=100)
anim.save("evolving_gr.gif", writer=writer)

plt.tight_layout()
plt.show()