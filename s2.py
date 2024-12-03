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

# Real charge at (a, 0) and image charge at (-a, 0)
Ex1, Ey1 = electric_field(q, a, 0, x, y)
Ex2, Ey2 = electric_field(-q, -a, 0, x, y)

# Total electric field components
Ex = Ex1 + Ex2
Ey = Ey1 + Ey2

# Masking the field to only show in the positive x-domain
mask = x > 0  # Mask where x is positive
Ex = np.where(mask, Ex, 0)
Ey = np.where(mask, Ey, 0)

# Plotting
fig, ax = plt.subplots(figsize=(8, 6))
ax.streamplot(x, y, Ex, Ey, color='grey', linewidth=0.8, density=1.5)
ax.plot([0, 0], [y_min, y_max], color='black', label='Grounded Conducting Plate')  # Conducting plate
ax.plot(a, 0, 'ro', label='Real Charge (q)')  # Real charge
ax.plot(-a, 0, 'bo', label='Image Charge (-q)')  # Image charge

# Adding text annotations for the labels
ax.text(a + 0.1, -0.1, 'q', color='red', fontsize=10, ha='left')
ax.text(-a - 0.15, -0.1, '-q', color='blue', fontsize=10, ha='left')

# Labels and title
ax.set_title('Point Charge Near a Grounded Conducting Plate (Image Charge)')
ax.set_xlabel('z-axis')
ax.set_ylabel('x-axis')
ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])
ax.grid(False)

plt.show()
