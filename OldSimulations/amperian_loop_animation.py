"""
Amperian Current Loop in Uniform Magnetic Field - Animation

Physics Model:
--------------
A circular current loop with magnetic moment μ (normal to loop plane) experiences
a torque τ = μ × B in a uniform magnetic field B. The potential energy is U = -μ·B = -μB cosθ.

Overdamped rotational dynamics (no inertia):
    dθ/dt = -γ sinθ

where γ is the relaxation rate and θ is the angle between μ and B.

Convention:
-----------
- B points in +y direction (upward on screen)
- θ is the polar angle: angle between μ and B (0° to 180°)
- φ is the azimuthal angle: rotation around the B axis (0° to 360°)
- θ = 0° means μ aligned with B (stable equilibrium) - loop appears horizontal (edge-on)
- θ = 90° means μ perpendicular to B - loop appears as full circle (face-on)
- θ = 180° means μ anti-aligned with B (unstable equilibrium) - loop appears horizontal again
- The current loop plane is ALWAYS perpendicular to μ

The loop relaxes from initial angle θ₀ toward alignment with B (θ → 0) while 
precessing around B with angular velocity ω_φ.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib import patches
import os

# ==================== PARAMETERS (easy to modify) ====================
gamma = 1.2              # Relaxation rate (1/time units)
theta0_deg = 120         # Initial polar angle in degrees
phi0_deg = 0             # Initial azimuthal angle in degrees
omega_phi = 1.5          # Angular velocity for precession around B (rad/time)

mu_mag = 1.0             # Magnitude of magnetic moment |μ|
B_mag = 1.0              # Magnitude of magnetic field |B|
steps = 220              # Number of animation frames (after initial pause)
dt = 0.04                # Time step for integration

initial_pause_frames = 45  # Number of frames to hold at initial state (1.5 sec at 30fps)

loop_width = 2.0         # Loop diameter (plotting units)
loop_height = 1.2        # Loop apparent height when tilted (plotting units)

output_filename = "amperian_loop.gif"  # Output animation file
fps = 30                 # Frames per second for animation
# ======================================================================

def integrate_dynamics(theta0, phi0, gamma, omega_phi, dt, steps, pause_frames=0):
    """
    Integrate coupled dynamics:
        dθ/dt = -γ sinθ         (relaxation toward alignment)
        dφ/dt = ω_φ             (precession around B axis)
    
    Args:
        theta0: Initial polar angle (radians)
        phi0: Initial azimuthal angle (radians)
        gamma: Relaxation rate
        omega_phi: Precession angular velocity
        dt: Time step
        steps: Number of integration steps
        pause_frames: Number of frames to hold at initial state before dynamics start
    
    Returns:
        times: array of time values
        thetas: array of θ values (in radians)
        phis: array of φ values (in radians)
    """
    # Add initial pause frames (hold at θ₀, φ₀)
    thetas = [theta0] * pause_frames
    phis = [phi0] * pause_frames
    times = [0.0] * pause_frames
    
    # Now integrate the dynamics
    theta = theta0
    phi = phi0
    thetas.append(theta)
    phis.append(phi)
    times.append(0.0)
    
    for i in range(steps - 1):
        dtheta_dt = -gamma * np.sin(theta)
        dphi_dt = omega_phi
        
        theta = theta + dtheta_dt * dt
        phi = phi + dphi_dt * dt
        
        thetas.append(theta)
        phis.append(phi)
        times.append(times[-1] + dt)
    
    return np.array(times), np.array(thetas), np.array(phis)

def draw_current_loop(ax, theta, phi, loop_width, loop_height):
    """
    Draw a circular current loop that is perpendicular (orthogonal) to the magnetic moment μ.
    
    The loop is a circle of radius R in 3D space, lying in the plane perpendicular to μ.
    We parametrize the circle, then project it onto the viewing plane (x-y screen).
    
    μ in 3D: μ = (sin(θ)cos(φ), cos(θ), sin(θ)sin(φ))
    Viewing from +z direction (looking down the z-axis toward origin)
    """
    radius = loop_width / 2
    
    # Step 1: Define μ (the magnetic moment) - normal to the loop plane
    mu = np.array([
        np.sin(theta) * np.cos(phi),  # μ_x
        np.cos(theta),                 # μ_y
        np.sin(theta) * np.sin(phi)    # μ_z
    ])
    
    # Step 2: Find two orthogonal unit vectors (e1, e2) that span the loop plane
    # These vectors must be perpendicular to μ and to each other
    
    # Choose e1: perpendicular to μ. We can pick any vector not parallel to μ,
    # then use Gram-Schmidt to make it perpendicular
    # Start with a candidate vector (try z-axis first, unless μ is parallel to z)
    if np.abs(mu[2]) < 0.9:  # μ is not too close to z-axis
        candidate = np.array([0, 0, 1])
    else:  # μ is close to z-axis, use x-axis instead
        candidate = np.array([1, 0, 0])
    
    # Make e1 perpendicular to μ using: e1 = candidate - (candidate·μ)μ
    e1 = candidate - np.dot(candidate, mu) * mu
    e1 = e1 / np.linalg.norm(e1)  # Normalize
    
    # e2 = μ × e1 (perpendicular to both μ and e1)
    e2 = np.cross(mu, e1)
    e2 = e2 / np.linalg.norm(e2)  # Normalize (should already be unit, but be safe)
    
    # Step 3: Parametrize the circle in 3D space
    # P(t) = radius * (cos(t) * e1 + sin(t) * e2) for t ∈ [0, 2π]
    n_points = 100
    t = np.linspace(0, 2*np.pi, n_points)
    
    # 3D coordinates of points on the circle
    circle_3d = radius * (np.outer(np.cos(t), e1) + np.outer(np.sin(t), e2))
    
    # Step 4: Project onto the x-y plane (viewing screen)
    # We're viewing from +z, so projection is just taking x and y coordinates
    circle_x = circle_3d[:, 0]  # x-coordinates on screen
    circle_y = circle_3d[:, 1]  # y-coordinates on screen
    
    # Step 5: Draw the loop
    ax.plot(circle_x, circle_y, 'b-', linewidth=2.5, zorder=5)
    
    # Step 6: Add arrows to indicate current direction at multiple points
    # Use the right-hand rule: fingers curl with current, thumb points along μ
    # Place arrows at multiple positions to show rotation clearly
    arrow_positions = [0, np.pi/2, np.pi, 3*np.pi/2]  # 4 arrows around the loop
    
    for arrow_t in arrow_positions:
        arrow_pos_3d = radius * (np.cos(arrow_t) * e1 + np.sin(arrow_t) * e2)
        arrow_x = arrow_pos_3d[0]
        arrow_y = arrow_pos_3d[1]
        
        # Tangent direction: dP/dt = radius * (-sin(t) * e1 + cos(t) * e2)
        # This gives the counterclockwise direction when viewed from μ
        arrow_tangent_3d = (-np.sin(arrow_t) * e1 + np.cos(arrow_t) * e2)
        arrow_dx = arrow_tangent_3d[0] * 0.2
        arrow_dy = arrow_tangent_3d[1] * 0.2
        
        # Only draw arrow if it's on the visible part of the loop
        if np.abs(arrow_y) > 0.15 or np.max(np.abs(circle_y)) > 0.3:
            ax.arrow(arrow_x, arrow_y, arrow_dx, arrow_dy,
                    head_width=0.12, head_length=0.08,
                    fc='darkblue', ec='darkblue', linewidth=1.2, zorder=6)

def draw_current_loop_xz(ax, theta, phi, loop_width, loop_height):
    """
    Draw a circular current loop projected onto the x-z plane (top-down view from +y).
    The loop is perpendicular (orthogonal) to the magnetic moment μ.
    This view looks down the B field direction.
    """
    radius = loop_width / 2
    
    # Step 1: Define μ (the magnetic moment) - normal to the loop plane
    mu = np.array([
        np.sin(theta) * np.cos(phi),  # μ_x
        np.cos(theta),                 # μ_y
        np.sin(theta) * np.sin(phi)    # μ_z
    ])
    
    # Step 2: Find two orthogonal unit vectors (e1, e2) that span the loop plane
    if np.abs(mu[2]) < 0.9:
        candidate = np.array([0, 0, 1])
    else:
        candidate = np.array([1, 0, 0])
    
    e1 = candidate - np.dot(candidate, mu) * mu
    e1 = e1 / np.linalg.norm(e1)
    
    e2 = np.cross(mu, e1)
    e2 = e2 / np.linalg.norm(e2)
    
    # Step 3: Parametrize the circle in 3D space
    n_points = 100
    t = np.linspace(0, 2*np.pi, n_points)
    circle_3d = radius * (np.outer(np.cos(t), e1) + np.outer(np.sin(t), e2))
    
    # Step 4: Project onto the x-z plane (viewing from +y, looking down B)
    # Take x (axis 0) and z (axis 2) coordinates
    circle_x = circle_3d[:, 0]  # x-coordinates (horizontal on this view)
    circle_z = circle_3d[:, 2]  # z-coordinates (vertical on this view)
    
    # Step 5: Draw the loop
    ax.plot(circle_x, circle_z, 'b-', linewidth=2.5, zorder=5)
    
    # Step 6: Add arrows to indicate current direction at multiple points
    # Use the right-hand rule: fingers curl with current, thumb points along μ
    # Place arrows at multiple positions to show rotation clearly
    arrow_positions = [0, np.pi/2, np.pi, 3*np.pi/2]  # 4 arrows around the loop
    
    for arrow_t in arrow_positions:
        arrow_pos_3d = radius * (np.cos(arrow_t) * e1 + np.sin(arrow_t) * e2)
        arrow_x = arrow_pos_3d[0]
        arrow_z = arrow_pos_3d[2]
        
        # Tangent direction: dP/dt = radius * (-sin(t) * e1 + cos(t) * e2)
        # This gives the counterclockwise direction when viewed from μ
        arrow_tangent_3d = (-np.sin(arrow_t) * e1 + np.cos(arrow_t) * e2)
        arrow_dx = -arrow_tangent_3d[0] * 0.2
        arrow_dz = -arrow_tangent_3d[2] * 0.2
        
        # Draw all arrows that are visible
        if np.max(np.abs(circle_x)) > 0.2 or np.max(np.abs(circle_z)) > 0.2:
            ax.arrow(arrow_x, arrow_z, arrow_dx, arrow_dz,
                    head_width=0.12, head_length=0.08,
                    fc='darkblue', ec='darkblue', linewidth=1.2, zorder=6)

def setup_plot():
    """Set up the figure with two subplots: x-y view (side) and x-z view (top-down)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left plot: x-y plane (view from +z) - side view
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('y', fontsize=12)
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    ax1.set_title('Side View (x-y plane, from +z)', fontsize=12, pad=10)
    
    # Right plot: x-z plane (view from +y) - top-down looking along B
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlabel('x', fontsize=12)
    ax2.set_ylabel('z', fontsize=12)
    ax2.axhline(y=0, color='k', linewidth=0.5)
    ax2.axvline(x=0, color='k', linewidth=0.5)
    ax2.set_title('Top-Down View (x-z plane, from +y)', fontsize=12, pad=10)
    
    return fig, ax1, ax2

def animate_frame(frame, times, thetas, phis, ax1, ax2, texts):
    """Update function for animation - draws x-y (side) and x-z (top-down) views."""
    theta = thetas[frame]
    phi = phis[frame]
    time = times[frame]
    
    # Calculate μ components
    mu_x = mu_mag * np.sin(theta) * np.cos(phi)
    mu_y = mu_mag * np.cos(theta)
    mu_z = mu_mag * np.sin(theta) * np.sin(phi)
    
    # ==== LEFT PLOT: x-y view (from +z) ====
    ax1.clear()
    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-2, 2)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('y', fontsize=12)
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=0, color='k', linewidth=0.5)
    ax1.set_title('View from +z (x-y plane)', fontsize=12, pad=10)
    
    # Draw B field
    ax1.arrow(1.5, -1.5, 0, 0.6, head_width=0.15, head_length=0.1,
             fc='red', ec='red', linewidth=2.5, zorder=10)
    ax1.text(1.5, -0.7, r'$\mathbf{B}$', fontsize=16, ha='center', color='red', weight='bold')
    
    # Draw loop
    draw_current_loop(ax1, theta, phi, loop_width, loop_height)
    
    # Draw μ
    ax1.arrow(0, 0, mu_x * 0.7, mu_y * 0.7, 
             head_width=0.15, head_length=0.15,
             fc='green', ec='green', linewidth=3, zorder=11)
    ax1.text(mu_x * 0.7 + 0.25 * mu_x / mu_mag, 
            mu_y * 0.7 + 0.25 * mu_y / mu_mag,
            r'$\boldsymbol{\mu}$', fontsize=16, ha='center', color='green', weight='bold')
    
    # ==== RIGHT PLOT: x-z view (from +y) - TOP-DOWN looking along B ====
    ax2.clear()
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlabel('x', fontsize=12)
    ax2.set_ylabel('z', fontsize=12)
    ax2.axhline(y=0, color='k', linewidth=0.5)
    ax2.axvline(x=0, color='k', linewidth=0.5)
    ax2.set_title('Top-Down View (x-z plane, from +y)', fontsize=12, pad=10)
    
    # Add indicator that +y (B field) points out of screen (toward viewer)
    # Draw a circle with a dot in the center (standard notation for "out of page")
    circle = plt.Circle((1.5, -1.5), 0.2, fill=False, edgecolor='red', linewidth=2.5, zorder=10)
    ax2.add_patch(circle)
    ax2.plot(1.5, -1.5, 'o', color='red', markersize=10, zorder=11)
    ax2.text(1.5, -1.8, r'$\mathbf{B}$ (out)', fontsize=12, ha='center', color='red', weight='bold')
    
    # Draw loop
    draw_current_loop_xz(ax2, theta, phi, loop_width, loop_height)
    
    # Draw μ (x-z projection - this is the projection onto the x-z plane)
    ax2.arrow(0, 0, mu_x * 0.7, mu_z * 0.7, 
             head_width=0.15, head_length=0.15,
             fc='green', ec='green', linewidth=3, zorder=11)
    # Position label for μ
    mu_xz_mag = np.sqrt(mu_x**2 + mu_z**2)
    if mu_xz_mag > 0.01:
        ax2.text(mu_x * 0.7 + 0.25 * mu_x / mu_xz_mag, 
                mu_z * 0.7 + 0.25 * mu_z / mu_xz_mag,
                r'$\boldsymbol{\mu}$', fontsize=16, ha='center', color='green', weight='bold')
    else:
        # μ is nearly aligned with B (pointing out of screen), show as a dot
        ax2.plot(0, 0, 'o', color='green', markersize=10, zorder=12)
        ax2.text(0.3, 0.3, r'$\boldsymbol{\mu}$', fontsize=16, ha='center', color='green', weight='bold')
    
    # Display text information (on left plot)
    theta_deg = np.degrees(theta)
    phi_deg = np.degrees(phi) % 360
    U = -mu_mag * B_mag * np.cos(theta)
    
    info_text = f'θ(t) = {theta_deg:.1f}°\nφ(t) = {phi_deg:.1f}°\nU(t) = {U:.2f}'
    ax1.text(-1.8, 1.7, info_text, fontsize=14, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            verticalalignment='top', family='monospace')
    
    ax1.text(-1.8, -1.7, f't = {time:.2f}', fontsize=12, 
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7),
            family='monospace')
    
    # Add main title
    ax1.figure.suptitle('Amperian Current Loop in Magnetic Field', 
                        fontsize=16, weight='bold', y=0.98)

def main():
    """Main function to create and save the animation."""
    print("Starting animation generation...")
    print(f"Parameters:")
    print(f"  gamma = {gamma}")
    print(f"  theta_0 = {theta0_deg} degrees")
    print(f"  phi_0 = {phi0_deg} degrees")
    print(f"  omega_phi = {omega_phi} rad/time")
    print(f"  |mu| = {mu_mag}")
    print(f"  |B| = {B_mag}")
    print(f"  frames = {steps}")
    print(f"  dt = {dt}")
    print(f"  initial_pause_frames = {initial_pause_frames}")
    
    # Convert initial angles to radians
    theta0 = np.radians(theta0_deg)
    phi0 = np.radians(phi0_deg)
    
    # Integrate the differential equations with initial pause
    times, thetas, phis = integrate_dynamics(theta0, phi0, gamma, omega_phi, dt, steps, 
                                             pause_frames=initial_pause_frames)
    
    total_frames = len(thetas)
    
    print(f"\nIntegration complete.")
    print(f"  Initial pause: {initial_pause_frames} frames ({initial_pause_frames/fps:.1f} seconds)")
    print(f"  Initial theta = {np.degrees(thetas[0]):.1f} degrees")
    print(f"  Initial phi = {np.degrees(phis[0]):.1f} degrees")
    print(f"  Final theta = {np.degrees(thetas[-1]):.1f} degrees")
    print(f"  Final phi = {np.degrees(phis[-1]) % 360:.1f} degrees")
    print(f"  Total simulation time = {times[-1]:.2f}")
    print(f"  Total frames = {total_frames}")
    
    # Set up the plot
    fig, ax1, ax2 = setup_plot()
    
    # Create empty text objects (will be updated in animate_frame)
    texts = {'theta': None, 'phi': None, 'energy': None}
    
    # Create animation
    print(f"\nCreating animation with {total_frames} frames...")
    anim = FuncAnimation(fig, animate_frame, frames=total_frames,
                        fargs=(times, thetas, phis, ax1, ax2, texts),
                        interval=1000/fps, blit=False, repeat=True)
    
    # Save animation
    print(f"Saving animation to '{output_filename}'...")
    writer = PillowWriter(fps=fps)
    anim.save(output_filename, writer=writer, dpi=100)
    
    print(f"\n[SUCCESS] Animation saved successfully to '{output_filename}'")
    print(f"  File size: {os.path.getsize(output_filename) / 1024:.1f} KB")
    print("\nTo view the animation, open the .gif file in any image viewer or web browser.")

if __name__ == "__main__":
    main()

