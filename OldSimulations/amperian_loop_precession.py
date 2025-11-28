"""
3D Animation of an Amperian Loop Precessing Around an External Magnetic Field

This script demonstrates how an Amperian loop (a current-carrying wire loop)
precesses around an external magnetic field while gradually aligning with it.
This behavior is analogous to a magnetic dipole in a magnetic field, where:

1. Precession: The loop's magnetic moment (normal vector) rotates around the
   field direction (z-axis) due to the torque τ = μ × B
2. Alignment: Over time, energy dissipation causes the tilt angle to decrease,
   bringing the loop's normal vector closer to the field direction

The animation shows both the fast precession motion and the slow alignment
process simultaneously, providing visual intuition for magnetic dipole dynamics.

Note: This script requires ffmpeg for MP4 output. Install with:
  - Windows: Download from https://ffmpeg.org/download.html
  - macOS: brew install ffmpeg
  - Linux: sudo apt-get install ffmpeg (or equivalent)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d import Axes3D


def create_loop(radius, n_points=100):
    """
    Create a 3D circular loop in the xy-plane.
    
    Parameters:
    -----------
    radius : float
        Radius of the loop
    n_points : int
        Number of points to discretize the circle
        
    Returns:
    --------
    points : ndarray
        Array of shape (n_points, 3) containing (x, y, z) coordinates
    """
    theta = np.linspace(0, 2 * np.pi, n_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.zeros_like(theta)
    return np.column_stack([x, y, z])


def rotate_points(points, axis, angle):
    """
    Rotate a set of 3D points about a given axis by a specified angle.
    Uses Rodrigues' rotation formula.
    
    Parameters:
    -----------
    points : ndarray
        Array of shape (n, 3) containing points to rotate
    axis : ndarray
        Axis of rotation (will be normalized)
    angle : float
        Rotation angle in radians
        
    Returns:
    --------
    rotated_points : ndarray
        Rotated points
    """
    axis = np.array(axis) / np.linalg.norm(axis)
    
    # Rodrigues' rotation formula
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    # Skew-symmetric matrix for cross product
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    # Rotation matrix
    R = (np.eye(3) * cos_a + 
         sin_a * K + 
         (1 - cos_a) * np.outer(axis, axis))
    
    return points @ R.T


def update(frame, original_loop_points, field_direction, ax, loop_line,
           normal_arrow_list, angle_text, total_frames,
           initial_tilt_angle, precession_rate, alignment_rate):
    """
    Update function for the animation.
    
    Parameters:
    -----------
    frame : int
        Current frame number
    original_loop_points : ndarray
        Original loop points in xy-plane
    field_direction : ndarray
        Direction of the external magnetic field (z-axis)
    ax : Axes3D
        The 3D axes
    loop_line : Line3D
        Line object representing the loop
    normal_arrow_list : list
        List to store arrow objects (will be cleared and redrawn)
    angle_text : Text
        Text object for displaying the tilt angle
    total_frames : int
        Total number of frames in the animation
    initial_tilt_angle : float
        Initial tilt angle in radians
    precession_rate : float
        Rate of precession (radians per frame)
    alignment_rate : float
        Rate of alignment (exponential decay factor)
    """
    # Calculate time progress (0 to 1)
    t = frame / total_frames
    
    # Use exponential decay for most of the animation, but smooth it out near zero
    # to prevent sudden jumps. Use a hybrid approach:
    # - Exponential decay for most of the range (fast alignment)
    # - Linear interpolation in the final 5% to ensure smooth transition to zero
    
    if t < 0.95:
        # Exponential decay for most of the animation (fast alignment)
        current_tilt_angle = initial_tilt_angle * np.exp(-alignment_rate * t)
    else:
        # Linear interpolation in final 5% for smooth transition to zero
        # Calculate the angle at t=0.95 using exponential decay
        angle_at_95 = initial_tilt_angle * np.exp(-alignment_rate * 0.95)
        # Linearly interpolate from angle_at_95 to 0 over the remaining 5% of frames
        linear_t = (t - 0.95) / 0.05  # Goes from 0 to 1 in final 5%
        current_tilt_angle = angle_at_95 * (1 - linear_t)
    
    # Ensure tilt reaches exactly zero only at the very last frame
    if frame >= total_frames - 1:
        current_tilt_angle = 0.0
    
    # Calculate precession angle (increases linearly around z-axis)
    precession_angle = precession_rate * frame
    
    # Start with original loop in xy-plane
    rotated_points = original_loop_points.copy()
    
    # Step 1: Tilt the loop by current_tilt_angle about x-axis
    # This creates the tilt away from the field direction (z-axis)
    tilt_axis = np.array([1, 0, 0])
    rotated_points = rotate_points(rotated_points, tilt_axis, current_tilt_angle)
    
    # Calculate normal vector after tilting (before precession)
    # Normal starts as [0, 0, 1] (pointing in +z), then tilts
    initial_normal = np.array([0, 0, 1])
    tilted_normal = rotate_points(initial_normal.reshape(1, -1), 
                                  tilt_axis, current_tilt_angle)[0]
    
    # Step 2: Rotate around the z-axis (field direction) for precession
    # This makes the tilted loop precess strictly around the z-axis
    z_axis = np.array([0, 0, 1])  # Precession axis is always z-axis
    rotated_points = rotate_points(rotated_points, z_axis, precession_angle)
    
    # Rotate the normal vector the same way (precess around z-axis)
    current_normal = rotate_points(tilted_normal.reshape(1, -1), 
                                   z_axis, precession_angle)[0]
    current_normal = current_normal / np.linalg.norm(current_normal)
    
    # Update loop line
    loop_line.set_data(rotated_points[:, 0], rotated_points[:, 1])
    loop_line.set_3d_properties(rotated_points[:, 2])
    
    # Calculate center for drawing
    center = np.mean(rotated_points, axis=0)
    
    # Clear and redraw normal vector
    for arrow in normal_arrow_list:
        arrow.remove()
    normal_arrow_list.clear()
    
    # Draw normal vector from center of loop
    normal_length = 0.8
    normal_end = center + normal_length * current_normal
    
    arrow = ax.quiver(center[0], center[1], center[2],
                     normal_end[0] - center[0],
                     normal_end[1] - center[1],
                     normal_end[2] - center[2],
                     color='green', arrow_length_ratio=0.2, linewidth=2.5)
    normal_arrow_list.append(arrow)
    
    # Update angle display
    angle_deg = np.degrees(current_tilt_angle)
    angle_text.set_text(f'Tilt Angle θ(t): {angle_deg:.1f}°')
    
    return loop_line, normal_arrow_list, angle_text


def main():
    """Main function to create and run the animation."""
    # Set font to Helvetica for all text in the plot
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans', 'sans-serif']
    
    # Parameters
    loop_radius = 1.0
    n_points = 100
    field_direction = np.array([0, 0, 1])  # Magnetic field in +z direction
    
    # Animation parameters
    initial_tilt_angle = np.pi / 2.5  # Start at ~72 degrees from field
    precession_rate = 0.08  # Radians per frame (controls precession speed)
    alignment_rate = 3.0  # Exponential decay rate for alignment (increased for faster alignment)
    interval = 20  # milliseconds between frames
    
    # Calculate total frames needed to reach near-zero tilt angle
    # With faster alignment rate, we need fewer frames but still want smooth animation
    # Calculate based on reaching 95% of the way (where we switch to linear interpolation)
    # At t=0.95, angle = initial_tilt * exp(-alpha * 0.95)
    # We want this to be small enough that linear interpolation to zero is smooth
    
    # Calculate what angle we'll have at t=0.95
    angle_at_95_percent = initial_tilt_angle * np.exp(-alignment_rate * 0.95)
    
    # We want enough frames so that the linear interpolation from this angle to zero
    # is smooth (at least 20-30 frames for the final 5%)
    # Total frames should allow for smooth animation throughout
    # With faster decay, we can use fewer total frames
    total_frames = 400  # Fixed frame count for consistent, smooth animation
    
    print(f"Animation will run for {total_frames} frames with faster alignment rate")
    
    # Create original loop in xy-plane
    original_loop_points = create_loop(loop_radius, n_points)
    
    # Create figure with single subplot
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Set static camera perspective
    ax.view_init(elev=25, azim=45)
    
    # Set axis limits
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_xlabel('x', fontsize=12, labelpad=10)
    ax.set_ylabel('y', fontsize=12, labelpad=10)
    ax.set_zlabel('z', fontsize=12, labelpad=10)
    ax.set_box_aspect([1, 1, 1])
    
    # Draw single magnetic field arrow (pointing in +z direction)
    field_arrow_length = 0.6
    field_arrow = ax.quiver(0, 0, 1.0, 0, 0, field_arrow_length,
                           color='blue', arrow_length_ratio=0.3, linewidth=2.5)
    
    # Initialize loop line
    # Start with initial tilt for display
    initial_tilt_axis = np.array([1, 0, 0])
    initial_loop = rotate_points(original_loop_points.copy(), 
                                 initial_tilt_axis, initial_tilt_angle)
    loop_line, = ax.plot(initial_loop[:, 0], initial_loop[:, 1], 
                        initial_loop[:, 2], 'r-', linewidth=2.5, label='Loop')
    
    # Initialize normal vector arrow (will be updated in animation)
    normal_arrow_list = []
    
    # Add initial normal vector
    center = np.mean(initial_loop, axis=0)
    initial_normal = np.array([0, 0, 1])
    tilted_normal = rotate_points(initial_normal.reshape(1, -1), 
                                  initial_tilt_axis, initial_tilt_angle)[0]
    
    normal_length = 0.8
    normal_end = center + normal_length * tilted_normal
    
    arrow = ax.quiver(center[0], center[1], center[2],
                     normal_end[0] - center[0],
                     normal_end[1] - center[1],
                     normal_end[2] - center[2],
                     color='green', arrow_length_ratio=0.2, linewidth=2.5)
    normal_arrow_list.append(arrow)
    
    # Add labels using text2D (outside the 3D scene)
    # Magnetic field label - positioned at top right
    ax.text2D(0.98, 0.95, "External Magnetic Field $\\vec{B}$",
             transform=ax.transAxes, fontsize=12, color='blue', weight='bold',
             horizontalalignment='right', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='blue'))
    
    # Loop normal label - positioned at top left
    ax.text2D(0.02, 0.95, "Loop Normal $\\hat{n}$",
             transform=ax.transAxes, fontsize=12, color='green', weight='bold',
             horizontalalignment='left', verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='green'))
    
    # Angle text - positioned at bottom left
    angle_text = ax.text2D(0.02, 0.02, 
                          f'Tilt Angle θ(t): {np.degrees(initial_tilt_angle):.1f}°',
                          transform=ax.transAxes, fontsize=11,
                          verticalalignment='bottom', horizontalalignment='left',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Add title
    ax.set_title('Amperian Loop Precession and Alignment', fontsize=14, pad=20, weight='bold')
    
    # Create animation (no repeat - stops naturally when tilt reaches zero)
    anim = FuncAnimation(fig, update, frames=total_frames, interval=interval,
                        fargs=(original_loop_points, field_direction, ax, loop_line,
                              normal_arrow_list, angle_text, total_frames,
                              initial_tilt_angle, precession_rate, alignment_rate),
                        blit=False, repeat=False)
    
    # Save animation as MP4
    print("Saving animation as MP4...")
    try:
        writer = FFMpegWriter(fps=50, metadata=dict(artist='Amperian Loop Precession'),
                             bitrate=1800)
        anim.save('amperian_loop_precession.mp4', writer=writer)
        print("Animation saved as 'amperian_loop_precession.mp4'")
    except Exception as e:
        print(f"ERROR: Could not save animation as MP4: {e}")
        print("\nffmpeg may not be installed. To install ffmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - macOS: brew install ffmpeg")
        print("  - Linux: sudo apt-get install ffmpeg (or equivalent)")
        print("\nDisplaying animation in window instead...")
        plt.show()
        return
    
    # Also display the animation
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
