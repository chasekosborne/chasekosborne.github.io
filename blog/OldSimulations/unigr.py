import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Wedge
from matplotlib.animation import PillowWriter


# ----- Parameters -----
N = 500             # Number of particles (reduce if animation is too heavy)
box_size = 1.0      # Size of the 2D box (square)
A = box_size**2     # Area of the box

# ----- Generate Ideal Gas Configuration -----
positions = np.random.rand(N, 2) * box_size

# Choose a reference particle (index 0)
ref_index = 0
ref_pos = positions[ref_index]

# ----- Define Periodic Distance Function -----
def periodic_distance(u, v, box_size=box_size):
    delta = u - v
    # Minimum image convention: bring the difference into [-box_size/2, box_size/2]
    delta = delta - box_size * np.round(delta / box_size)
    return np.sqrt(np.sum(delta**2))

# ----- Compute Distances from Reference Particle -----
# (Exclude the reference particle itself)
distances = np.array([periodic_distance(ref_pos, pos, box_size) 
                      for i, pos in enumerate(positions) if i != ref_index])

# ----- Define Radial Bins -----
r_max = box_size / 2.0
num_bins = 50
bins = np.linspace(0, r_max, num_bins + 1)
dr = bins[1] - bins[0]
bin_centers = (bins[:-1] + bins[1:]) / 2

# Density from the viewpoint of the reference (using N-1 because the ref. is excluded)
density = (N - 1) / A

# ----- Set Up the Figure and Axes -----
fig, (ax_box, ax_gr) = plt.subplots(1, 2, figsize=(12, 6))

# --- Left: Simulation Box ---
ax_box.set_xlim(0, box_size)
ax_box.set_ylim(0, box_size)
ax_box.set_aspect('equal')
ax_box.set_title("Simulation Box")

# Plot all particles
scat = ax_box.scatter(positions[:, 0], positions[:, 1], s=20, color='blue', alpha=0.5)
# Highlight the reference particle in red
ref_point, = ax_box.plot(ref_pos[0], ref_pos[1], 'ro', markersize=8)

# Create an annulus (using a Wedge with full circle) to show the current radial bin.
# Initially set to the first bin.
annulus = Wedge(ref_pos, bins[1], 0, 360, width=dr, edgecolor='royalblue', facecolor='none', lw=2)
ax_box.add_patch(annulus)

# --- Right: g(r) Plot ---
ax_gr.set_xlim(0, r_max)
ax_gr.set_ylim(0, 2)
ax_gr.set_xlabel("r")
ax_gr.set_ylabel("g(r)")
ax_gr.set_title("Radial Distribution Function")
ax_gr.axhline(1, color='red', linestyle='--', label='g(r)=1')

# Line object to update the computed g(r) values
gr_line, = ax_gr.plot([], [], 'bo-', label='g(r) computed')
ax_gr.legend()

# List to store computed g(r) values for each bin as we progress
g_r_values = []

# ----- Animation Functions -----
def init():
    gr_line.set_data([], [])
    return scat, ref_point, annulus, gr_line

def update(frame):
    # Frame index corresponds to the current bin (0 to num_bins-1)
    r_low = bins[frame]
    r_high = bins[frame + 1]
    
    # Update the annulus to represent the current bin
    annulus.set_radius(r_high)
    annulus.set_width(dr)
    
    # Update particle colors: highlight those within the current annulus in orange.
    new_colors = []
    for pos in positions:
        d = periodic_distance(ref_pos, pos, box_size)
        if r_low <= d < r_high:
            new_colors.append('orange')
        else:
            new_colors.append('blue')
    scat.set_color(new_colors)
    
    # Count the number of particles (from the reference) in the current annulus.
    count = np.sum((distances >= r_low) & (distances < r_high))
    # Expected number in the annulus = density * (area of annulus)
    expected = density * (np.pi * (r_high**2 - r_low**2))
    g_r = count / expected if expected > 0 else 0
    g_r_values.append(g_r)
    
    # Update the g(r) plot on the right
    x_data = bin_centers[:frame+1]
    y_data = g_r_values
    gr_line.set_data(x_data, y_data)
    
    # Optionally update the title of the g(r) plot to show the current value
    ax_gr.set_title(f"g(r) at r={bin_centers[frame]:.2f}: {g_r:.2f}")
    
    return scat, ref_point, annulus, gr_line

# Create the animation: each frame lasts 500ms.
anim = FuncAnimation(fig, update, frames=range(num_bins),
                     init_func=init, blit=True, interval=500, repeat=False)

# Save the animation as a GIF file
writer = PillowWriter(fps=4)  # Adjust fps (frames per second) as needed
anim.save("radial_distribution.gif", writer=writer)

plt.tight_layout()
plt.show()