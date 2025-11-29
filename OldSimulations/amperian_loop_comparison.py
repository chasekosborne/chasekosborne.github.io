"""
3D Animation Comparison: Amperian Loop with and without Precession

This script demonstrates two different behaviors of an Amperian loop in an external
magnetic field:

Left plot: Precession + Alignment
- The loop's normal vector precesses around the z-axis (field direction)
- Simultaneously, the tilt angle decreases, bringing the loop into alignment
- This represents realistic magnetic dipole dynamics

Right plot: Alignment Only (No Precession)
- The loop simply rotates to align with the field
- No precession motion - the loop does not rotate around the z-axis
- The normal vector moves directly toward the field direction

This comparison helps visualize the difference between precessing and non-precessing
magnetic dipole alignment.

Note: This script exports animations in multiple formats:
  - MP4: Requires ffmpeg. Install with:
    * Windows: Download from https://ffmpeg.org/download.html
    * macOS: brew install ffmpeg
    * Linux: sudo apt-get install ffmpeg (or equivalent)
  - GIF: Requires Pillow (PIL). Install with: pip install pillow
  - HTML: JavaScript-based animation that runs in web browsers (built-in to matplotlib)
  
  For animated SVG: Matplotlib doesn't natively support animated SVG for 3D plots.
  For best web integration, the HTML export is recommended, or consider creating
  a custom JavaScript/Three.js version for full interactivity.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter, HTMLWriter
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


def update(frame, original_loop_points, field_direction, ax1, ax2,
           loop_line1, loop_line2, normal_arrow_list1, normal_arrow_list2,
           angle_text1, angle_text2, total_frames,
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
    ax1, ax2 : Axes3D
        The two 3D axes (left: precession+alignment, right: alignment only)
    loop_line1, loop_line2 : Line3D
        Line objects representing the loops
    normal_arrow_list1, normal_arrow_list2 : list
        Lists to store arrow objects (will be cleared and redrawn)
    angle_text1, angle_text2 : Text
        Text objects for displaying the tilt angle
    total_frames : int
        Total number of frames in the animation
    initial_tilt_angle : float
        Initial tilt angle in radians
    precession_rate : float
        Rate of precession (radians per frame) - only used for left plot
    alignment_rate : float
        Rate of alignment (exponential decay factor)
    """
    # Calculate time progress (0 to 1)
    t = frame / total_frames
    
    # Calculate current tilt angle (same for both plots)
    # Use exponential decay for most of the animation, but smooth it out near zero
    if t < 0.95:
        # Exponential decay for most of the animation (fast alignment)
        current_tilt_angle = initial_tilt_angle * np.exp(-alignment_rate * t)
    else:
        # Linear interpolation in final 5% for smooth transition to zero
        angle_at_95 = initial_tilt_angle * np.exp(-alignment_rate * 0.95)
        linear_t = (t - 0.95) / 0.05
        current_tilt_angle = angle_at_95 * (1 - linear_t)
    
    # Ensure tilt reaches exactly zero only at the very last frame
    if frame >= total_frames - 1:
        current_tilt_angle = 0.0
    
    # Update both plots
    for plot_idx, (ax, loop_line, normal_arrow_list, angle_text, use_precession) in enumerate(
        [(ax1, loop_line1, normal_arrow_list1, angle_text1, True),
         (ax2, loop_line2, normal_arrow_list2, angle_text2, False)]):
        
        # Calculate precession angle (only for left plot)
        if use_precession:
            precession_angle = precession_rate * frame
        else:
            precession_angle = 0.0  # No precession for right plot
        
        # Start with original loop in xy-plane
        rotated_points = original_loop_points.copy()
        
        # Step 1: Tilt the loop by current_tilt_angle about x-axis
        tilt_axis = np.array([1, 0, 0])
        rotated_points = rotate_points(rotated_points, tilt_axis, current_tilt_angle)
        
        # Calculate normal vector after tilting (before precession)
        initial_normal = np.array([0, 0, 1])
        tilted_normal = rotate_points(initial_normal.reshape(1, -1), 
                                      tilt_axis, current_tilt_angle)[0]
        
        # Step 2: Rotate around the z-axis (only if precession is enabled)
        z_axis = np.array([0, 0, 1])
        rotated_points = rotate_points(rotated_points, z_axis, precession_angle)
        
        # Rotate the normal vector the same way
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
    
    return loop_line1, loop_line2, normal_arrow_list1, normal_arrow_list2, angle_text1, angle_text2


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
    alignment_rate = 3.0  # Exponential decay rate for alignment
    interval = 20  # milliseconds between frames
    total_frames = 400  # Fixed frame count for consistent, smooth animation
    
    print(f"Animation will run for {total_frames} frames")
    
    # Create original loop in xy-plane
    original_loop_points = create_loop(loop_radius, n_points)
    
    # Create figure with two subplots side-by-side
    fig = plt.figure(figsize=(20, 10))
    ax1 = fig.add_subplot(121, projection='3d')  # Left: Precession + Alignment
    ax2 = fig.add_subplot(122, projection='3d')  # Right: Alignment Only
    
    # Set static camera perspective for both
    for ax in [ax1, ax2]:
        ax.view_init(elev=25, azim=45)
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_zlim([-1.5, 1.5])
        ax.set_xlabel('x', fontsize=12, labelpad=10)
        ax.set_ylabel('y', fontsize=12, labelpad=10)
        ax.set_zlabel('z', fontsize=12, labelpad=10)
        ax.set_box_aspect([1, 1, 1])
    
    # Draw magnetic field arrows for both plots
    field_arrow_length = 0.6
    for ax in [ax1, ax2]:
        ax.quiver(0, 0, 1.0, 0, 0, field_arrow_length,
                 color='blue', arrow_length_ratio=0.3, linewidth=2.5)
    
    # Initialize loop lines for both plots
    initial_tilt_axis = np.array([1, 0, 0])
    initial_loop = rotate_points(original_loop_points.copy(), 
                                 initial_tilt_axis, initial_tilt_angle)
    
    loop_line1, = ax1.plot(initial_loop[:, 0], initial_loop[:, 1], 
                           initial_loop[:, 2], 'r-', linewidth=2.5, label='Loop')
    loop_line2, = ax2.plot(initial_loop[:, 0], initial_loop[:, 1], 
                           initial_loop[:, 2], 'r-', linewidth=2.5, label='Loop')
    
    # Initialize normal vector arrows for both plots
    normal_arrow_list1 = []
    normal_arrow_list2 = []
    
    center = np.mean(initial_loop, axis=0)
    initial_normal = np.array([0, 0, 1])
    tilted_normal = rotate_points(initial_normal.reshape(1, -1), 
                                  initial_tilt_axis, initial_tilt_angle)[0]
    
    normal_length = 0.8
    normal_end = center + normal_length * tilted_normal
    
    for ax, normal_arrow_list in [(ax1, normal_arrow_list1), (ax2, normal_arrow_list2)]:
        arrow = ax.quiver(center[0], center[1], center[2],
                         normal_end[0] - center[0],
                         normal_end[1] - center[1],
                         normal_end[2] - center[2],
                         color='green', arrow_length_ratio=0.2, linewidth=2.5)
        normal_arrow_list.append(arrow)
    
    # Add labels for left plot (Precession + Alignment)
    ax1.text2D(0.98, 0.95, "External Magnetic Field $\\vec{B}$",
              transform=ax1.transAxes, fontsize=11, color='blue', weight='bold',
              horizontalalignment='right', verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='blue'))
    
    ax1.text2D(0.02, 0.95, "Loop Normal $\\hat{n}$",
              transform=ax1.transAxes, fontsize=11, color='green', weight='bold',
              horizontalalignment='left', verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='green'))
    
    angle_text1 = ax1.text2D(0.02, 0.02, 
                            f'Tilt Angle θ(t): {np.degrees(initial_tilt_angle):.1f}°',
                            transform=ax1.transAxes, fontsize=10,
                            verticalalignment='bottom', horizontalalignment='left',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax1.set_title('Precession + Alignment', fontsize=13, pad=15, weight='bold')
    
    # Add labels for right plot (Alignment Only)
    ax2.text2D(0.98, 0.95, "External Magnetic Field $\\vec{B}$",
              transform=ax2.transAxes, fontsize=11, color='blue', weight='bold',
              horizontalalignment='right', verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='blue'))
    
    ax2.text2D(0.02, 0.95, "Loop Normal $\\hat{n}$",
              transform=ax2.transAxes, fontsize=11, color='green', weight='bold',
              horizontalalignment='left', verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='green'))
    
    angle_text2 = ax2.text2D(0.02, 0.02, 
                            f'Tilt Angle θ(t): {np.degrees(initial_tilt_angle):.1f}°',
                            transform=ax2.transAxes, fontsize=10,
                            verticalalignment='bottom', horizontalalignment='left',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax2.set_title('Alignment Only (No Precession)', fontsize=13, pad=15, weight='bold')
    
    # Add overall figure title
    fig.suptitle('Amperian Loop: Precession vs. Direct Alignment', 
                fontsize=16, weight='bold', y=0.98)
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=total_frames, interval=interval,
                        fargs=(original_loop_points, field_direction, ax1, ax2,
                              loop_line1, loop_line2, normal_arrow_list1, normal_arrow_list2,
                              angle_text1, angle_text2, total_frames,
                              initial_tilt_angle, precession_rate, alignment_rate),
                        blit=False, repeat=False)
    
    # Save animation as MP4
    print("Saving animation as MP4...")
    mp4_saved = False
    try:
        writer = FFMpegWriter(fps=50, metadata=dict(artist='Amperian Loop Comparison'),
                             bitrate=1800)
        anim.save('amperian_loop_comparison.mp4', writer=writer)
        print("Animation saved as 'amperian_loop_comparison.mp4'")
        mp4_saved = True
    except Exception as e:
        print(f"ERROR: Could not save animation as MP4: {e}")
        print("\nffmpeg may not be installed. To install ffmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - macOS: brew install ffmpeg")
        print("  - Linux: sudo apt-get install ffmpeg (or equivalent)")
    
    # Save animation as GIF
    print("\nSaving animation as GIF...")
    try:
        writer_gif = PillowWriter(fps=50)
        anim.save('amperian_loop_comparison.gif', writer=writer_gif)
        print("Animation saved as 'amperian_loop_comparison.gif'")
    except Exception as e:
        print(f"ERROR: Could not save animation as GIF: {e}")
        print("\nPillow (PIL) may not be installed. To install:")
        print("  pip install pillow")
    
    # Save animation as HTML (JavaScript-based, runs in browser)
    print("\nSaving animation as HTML (web-compatible)...")
    try:
        writer_html = HTMLWriter(fps=50)
        anim.save('amperian_loop_comparison.html', writer=writer_html)
        print("Animation saved as 'amperian_loop_comparison.html'")
        print("  Note: This HTML file can be opened in a web browser and embedded in websites.")
        print("  However, 3D plots may have limited interactivity in HTML export.")
    except Exception as e:
        print(f"ERROR: Could not save animation as HTML: {e}")
    
    # Note about animated SVG
    print("\n" + "="*60)
    print("Note about Animated SVG:")
    print("="*60)
    print("Matplotlib doesn't natively support animated SVG export for 3D plots.")
    print("For best web compatibility, consider:")
    print("  1. Using the HTML export above (JavaScript-based)")
    print("  2. Creating a custom JavaScript/Three.js version for full interactivity")
    print("  3. Using the GIF export for simple embedding")
    print("="*60 + "\n")
    
    # If both exports failed, display animation instead
    if not mp4_saved:
        print("\nDisplaying animation in window instead...")
        plt.show()
        return
    
    # Also display the animation
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()

