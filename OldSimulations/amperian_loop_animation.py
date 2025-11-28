"""
3D Animation of an Amperian Loop Aligning with an External Magnetic Field

This script demonstrates how an Amperian loop (a current-carrying wire loop)
rotates to align itself with an external magnetic field. The alignment occurs
because the magnetic field exerts a torque on the loop, causing it to rotate
until the loop's normal vector is parallel to the magnetic field direction,
minimizing the magnetic potential energy.

Physics: The torque on a magnetic dipole (loop) is τ = μ × B, where μ is the
magnetic moment (proportional to the loop's area and current) and B is the
external magnetic field. The loop rotates to align μ with B.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
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


def rotate_loop(points, angle, axis):
    """
    Rotate a set of 3D points about a given axis by a specified angle.
    
    Parameters:
    -----------
    points : ndarray
        Array of shape (n, 3) containing points to rotate
    angle : float
        Rotation angle in radians
    axis : ndarray
        Axis of rotation (will be normalized)
        
    Returns:
    --------
    rotated_points : ndarray
        Rotated points
    """
    axis = np.array(axis) / np.linalg.norm(axis)
    
    # Rodrigues' rotation formula
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    
    # Rotation matrix components
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    R = (np.eye(3) * cos_a + 
         sin_a * K + 
         (1 - cos_a) * np.outer(axis, axis))
    
    return points @ R.T


def draw_field_vectors(ax, field_direction=np.array([0, 0, 1]), 
                       grid_size=5, vector_length=0.3):
    """
    Draw parallel magnetic field vectors in 3D space.
    
    Parameters:
    -----------
    ax : Axes3D
        The 3D axes to draw on
    field_direction : ndarray
        Direction of the magnetic field (will be normalized)
    grid_size : int
        Number of vectors along each dimension (creates grid_size^2 vectors)
    vector_length : float
        Length of the arrow vectors
    """
    field_direction = field_direction / np.linalg.norm(field_direction)
    
    # Create a grid of starting points
    x_range = np.linspace(-2, 2, grid_size)
    y_range = np.linspace(-2, 2, grid_size)
    z_range = np.linspace(-1, 1, grid_size)
    
    # Draw vectors in a plane perpendicular to the field direction
    # For a field in +z direction, draw vectors in xy-plane
    if np.abs(field_direction[2]) > 0.9:  # Field is mostly in z-direction
        X, Y = np.meshgrid(x_range, y_range)
        Z = np.zeros_like(X)
        for i in range(grid_size):
            for j in range(grid_size):
                start = np.array([X[i, j], Y[i, j], Z[i, j]])
                end = start + vector_length * field_direction
                ax.quiver(start[0], start[1], start[2],
                         end[0] - start[0], end[1] - start[1], end[2] - start[2],
                         color='blue', arrow_length_ratio=0.3, linewidth=1.5)
    else:
        # Generic case: draw vectors in a plane
        for z_val in z_range:
            X, Y = np.meshgrid(x_range, y_range)
            for i in range(grid_size):
                for j in range(grid_size):
                    start = np.array([X[i, j], Y[i, j], z_val])
                    end = start + vector_length * field_direction
                    ax.quiver(start[0], start[1], start[2],
                             end[0] - start[0], end[1] - start[1], end[2] - start[2],
                             color='blue', arrow_length_ratio=0.3, linewidth=1.5)


def calculate_angle_between_vectors(v1, v2):
    """
    Calculate the angle between two vectors in radians.
    
    Parameters:
    -----------
    v1, v2 : ndarray
        Two vectors
        
    Returns:
    --------
    angle : float
        Angle in radians
    """
    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)
    dot_product = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
    return np.arccos(dot_product)


def update(frame, original_loop_points, initial_tilt_angle, initial_tilt_axis,
           field_direction, ax1, ax2, loop_line1, loop_line2, normal_arrow1, normal_arrow2,
           angle_text1, angle_text2, total_frames):
    """
    Update function for the animation.
    
    Parameters:
    -----------
    frame : int
        Current frame number
    original_loop_points : ndarray
        Original loop points in xy-plane (will be rotated)
    initial_tilt_angle : float
        Initial tilt angle in radians
    initial_tilt_axis : ndarray
        Axis for initial tilt rotation
    field_direction : ndarray
        Direction of the external magnetic field
    ax1, ax2 : Axes3D
        The two subplot axes
    loop_line1, loop_line2 : Line3DCollection
        Line objects representing the loop in each subplot
    normal_arrow1, normal_arrow2 : list
        Lists to store arrow objects (will be cleared and redrawn)
    angle_text1, angle_text2 : Text
        Text objects for displaying the angle
    total_frames : int
        Total number of frames in the animation
    """
    # Calculate rotation progress (0 to 1)
    progress = frame / total_frames
    
    # Use smooth easing function (ease-in-out)
    eased_progress = 0.5 * (1 - np.cos(np.pi * progress))
    
    # Calculate initial normal after tilting
    initial_normal = np.array([0, np.sin(initial_tilt_angle), np.cos(initial_tilt_angle)])
    
    # Calculate current angle (from initial tilt to aligned)
    initial_angle = calculate_angle_between_vectors(initial_normal, field_direction)
    current_angle = initial_angle * (1 - eased_progress)
    
    # Calculate rotation axis for alignment (perpendicular to both initial normal and field)
    rotation_axis = np.cross(initial_normal, field_direction)
    if np.linalg.norm(rotation_axis) < 1e-6:
        # Vectors are already parallel/antiparallel
        rotation_axis = np.array([1, 0, 0])
    else:
        rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
    
    # Apply rotations: first initial tilt, then alignment rotation
    # Start with original loop in xy-plane
    rotated_points = original_loop_points.copy()
    # Apply initial tilt
    rotated_points = rotate_loop(rotated_points, initial_tilt_angle, initial_tilt_axis)
    # Apply alignment rotation
    alignment_angle = initial_angle * eased_progress
    rotated_points = rotate_loop(rotated_points, alignment_angle, rotation_axis)
    
    # Calculate current normal vector
    # Normal is perpendicular to the loop plane, pointing along the rotation
    center = np.mean(rotated_points, axis=0)
    # Use two points on the loop to define the plane
    v1 = rotated_points[0] - center
    v2 = rotated_points[len(rotated_points)//4] - center
    current_normal = np.cross(v1, v2)
    current_normal = current_normal / np.linalg.norm(current_normal)
    
    # Update loop lines
    loop_line1.set_data(rotated_points[:, 0], rotated_points[:, 1])
    loop_line1.set_3d_properties(rotated_points[:, 2])
    
    loop_line2.set_data(rotated_points[:, 0], rotated_points[:, 1])
    loop_line2.set_3d_properties(rotated_points[:, 2])
    
    # Clear and redraw normal vectors
    for arrow in normal_arrow1:
        arrow.remove()
    normal_arrow1.clear()
    
    for arrow in normal_arrow2:
        arrow.remove()
    normal_arrow2.clear()
    
    # Draw normal vector from center of loop
    normal_length = 0.8
    center = np.mean(rotated_points, axis=0)
    normal_end = center + normal_length * current_normal
    
    arrow1 = ax1.quiver(center[0], center[1], center[2],
                       normal_end[0] - center[0],
                       normal_end[1] - center[1],
                       normal_end[2] - center[2],
                       color='green', arrow_length_ratio=0.2, linewidth=2.5)
    normal_arrow1.append(arrow1)
    
    arrow2 = ax2.quiver(center[0], center[1], center[2],
                       normal_end[0] - center[0],
                       normal_end[1] - center[1],
                       normal_end[2] - center[2],
                       color='green', arrow_length_ratio=0.2, linewidth=2.5)
    normal_arrow2.append(arrow2)
    
    # Update angle display
    angle_deg = np.degrees(current_angle)
    angle_text1.set_text(f'Tilt Angle: {angle_deg:.1f}°')
    angle_text2.set_text(f'Tilt Angle: {angle_deg:.1f}°')
    
    # Rotate the right subplot camera (azimuth changes)
    ax2.view_init(elev=30, azim=45 + frame * 360 / total_frames)
    
    return loop_line1, loop_line2, normal_arrow1, normal_arrow2, angle_text1, angle_text2


def main():
    """Main function to create and run the animation."""
    # Parameters
    loop_radius = 1.0
    n_points = 100
    field_direction = np.array([0, 0, 1])  # Magnetic field in +z direction
    initial_tilt_angle = np.pi / 3  # Start at 60 degrees from field
    
    # Create original loop in xy-plane (normal pointing in +z)
    original_loop_points = create_loop(loop_radius, n_points)
    
    # Calculate initial normal after tilting (rotate about x-axis)
    initial_normal = np.array([0, np.sin(initial_tilt_angle), np.cos(initial_tilt_angle)])
    initial_rotation_axis = np.array([1, 0, 0])
    
    # Create initial tilted loop for display
    loop_points = rotate_loop(original_loop_points.copy(), initial_tilt_angle, initial_rotation_axis)
    
    # Create figure with two subplots
    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')
    
    # Set fixed perspective for left subplot
    ax1.view_init(elev=30, azim=45)
    
    # Set initial perspective for right subplot (will rotate during animation)
    ax2.view_init(elev=30, azim=45)
    
    # Set axis limits
    for ax in [ax1, ax2]:
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_zlim([-1.5, 1.5])
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_zlabel('z', fontsize=12)
        ax.set_box_aspect([1, 1, 1])
    
    # Draw magnetic field vectors
    draw_field_vectors(ax1, field_direction, grid_size=4, vector_length=0.4)
    draw_field_vectors(ax2, field_direction, grid_size=4, vector_length=0.4)
    
    # Add field direction label (single arrow at top)
    field_arrow_length = 0.5
    ax1.quiver(0, 0, 1.2, 0, 0, field_arrow_length,
              color='blue', arrow_length_ratio=0.3, linewidth=2)
    ax1.text(0.2, 0.2, 1.5, "External Magnetic Field $\\vec{B}$", 
            fontsize=11, color='blue')
    
    ax2.quiver(0, 0, 1.2, 0, 0, field_arrow_length,
              color='blue', arrow_length_ratio=0.3, linewidth=2)
    ax2.text(0.2, 0.2, 1.5, "External Magnetic Field $\\vec{B}$", 
            fontsize=11, color='blue')
    
    # Initialize loop lines
    loop_line1, = ax1.plot(loop_points[:, 0], loop_points[:, 1], 
                           loop_points[:, 2], 'r-', linewidth=2.5, label='Loop')
    loop_line2, = ax2.plot(loop_points[:, 0], loop_points[:, 1], 
                           loop_points[:, 2], 'r-', linewidth=2.5, label='Loop')
    
    # Initialize normal vector arrows (will be updated in animation)
    normal_arrow1 = []
    normal_arrow2 = []
    
    # Calculate initial normal after tilting
    initial_normal_calc = np.array([0, np.sin(initial_tilt_angle), np.cos(initial_tilt_angle)])
    
    # Add initial normal vector
    center = np.mean(loop_points, axis=0)
    normal_length = 0.8
    normal_end = center + normal_length * initial_normal_calc
    
    arrow1 = ax1.quiver(center[0], center[1], center[2],
                       normal_end[0] - center[0],
                       normal_end[1] - center[1],
                       normal_end[2] - center[2],
                       color='green', arrow_length_ratio=0.2, linewidth=2.5)
    normal_arrow1.append(arrow1)
    
    arrow2 = ax2.quiver(center[0], center[1], center[2],
                       normal_end[0] - center[0],
                       normal_end[1] - center[1],
                       normal_end[2] - center[2],
                       color='green', arrow_length_ratio=0.2, linewidth=2.5)
    normal_arrow2.append(arrow2)
    
    # Add normal vector label
    ax1.text(normal_end[0] + 0.1, normal_end[1] + 0.1, normal_end[2] + 0.1,
            "Loop Normal $\\hat{n}$", fontsize=11, color='green')
    ax2.text(normal_end[0] + 0.1, normal_end[1] + 0.1, normal_end[2] + 0.1,
            "Loop Normal $\\hat{n}$", fontsize=11, color='green')
    
    # Add angle text
    initial_angle = calculate_angle_between_vectors(initial_normal_calc, field_direction)
    angle_text1 = ax1.text2D(0.02, 0.98, f'Tilt Angle: {np.degrees(initial_angle):.1f}°',
                            transform=ax1.transAxes, fontsize=11,
                            verticalalignment='top', bbox=dict(boxstyle='round', 
                            facecolor='wheat', alpha=0.8))
    angle_text2 = ax2.text2D(0.02, 0.98, f'Tilt Angle: {np.degrees(initial_angle):.1f}°',
                            transform=ax2.transAxes, fontsize=11,
                            verticalalignment='top', bbox=dict(boxstyle='round', 
                            facecolor='wheat', alpha=0.8))
    
    # Add subplot titles
    ax1.set_title('Fixed Perspective (elev=30°, azim=45°)', fontsize=12, pad=20)
    ax2.set_title('Rotating Perspective', fontsize=12, pad=20)
    
    # Animation parameters
    total_frames = 200
    interval = 50  # milliseconds between frames
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=total_frames, interval=interval,
                        fargs=(original_loop_points, initial_tilt_angle, initial_rotation_axis,
                              field_direction, ax1, ax2, loop_line1, loop_line2,
                              normal_arrow1, normal_arrow2,
                              angle_text1, angle_text2, total_frames),
                        blit=False, repeat=True)
    
    # Save animation
    print("Saving animation...")
    try:
        writer = FFMpegWriter(fps=20, metadata=dict(artist='Amperian Loop Animation'),
                             bitrate=1800)
        anim.save('amperian_loop_animation.mp4', writer=writer)
        print("Animation saved as 'amperian_loop_animation.mp4'")
    except Exception as e:
        print(f"FFmpeg not available ({e}), trying PillowWriter (GIF)...")
        try:
            writer = PillowWriter(fps=20)
            anim.save('amperian_loop_animation.gif', writer=writer)
            print("Animation saved as 'amperian_loop_animation.gif'")
        except Exception as e2:
            print(f"Could not save animation: {e2}")
            print("Displaying animation in window instead...")
            plt.show()
            return
    
    # Also display the animation
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()

