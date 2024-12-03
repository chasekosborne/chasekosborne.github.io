import numpy as np
import matplotlib.pyplot as plt

# Constants
q = 1.0  # Charge magnitude (arbitrary units)
a = 1.0  # Distance of the charge from the conducting plate

# Grid setup
x_min, x_max = -2 * a, 2 * a
y_min, y_max = -2 * a, 2 * a
x, y = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))

# Electric field components due to a charge at (a, 0)
def electric_field(q, x0, y0, x, y):
    r_squared = (x - x0)**2 + (y - y0)**2
    r_cubed = np.sqrt(r_squared) ** 3
    Ex = q * (x - x0) / r_cubed
    Ey = q * (y - y0) / r_cubed
    return Ex, Ey

# Electric field from only the positive charge at (a, 0)
Ex, Ey = electric_field(q, a, 0, x, y)

# Plotting
fig, ax = plt.subplots(figsize=(8, 6))
ax.streamplot(x, y, Ex, Ey, color='grey', linewidth=0.8, density=1.5)
ax.plot(a, 0, 'ro', label='Real Charge (q)')  # Real charge
ax.plot([0, 0], [y_min, y_max], color='black', linestyle='-', label='Conducting Plate')  # Conducting plate (dashed)

# Adding text annotation for the positive charge
ax.text(a + 0.05, -0.3, 'q', color='red', fontsize=10, ha='left')

# Labels and title
ax.set_title('Point Charge Near a Grounded Conducting Plate (Initial Guess)')
ax.set_xlabel('z-axis')
ax.set_ylabel('x-axis')
ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])
ax.grid(False)

plt.show()
