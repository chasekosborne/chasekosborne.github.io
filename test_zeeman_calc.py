#!/usr/bin/env python3
import math

# Physical constants
e = 1.602176634e-19  # C
m_e = 9.1093837015e-31  # kg
c = 2.99792458e8  # m/s
h = 6.62607015e-34  # J·s
hbar = h / (2 * math.pi)
mu_B = 9.274009994e-24  # J/T (Bohr magneton)
B = 1.0  # Tesla

# Wavelengths
D1_wavelength = 589.6  # nm
D2_wavelength = 589.0  # nm

# g-factors
g_lower = 2.0023
g_D1_upper = 2.0 / 3.0
g_D2_upper = 4.0 / 3.0

# Standard Zeeman formula: ΔE = μ_B * B * (g_u m_J,u - g_l m_J,l)
# Then: Δλ = - (λ²/(hc)) * ΔE
# Or: Δλ = - (λ²/(hc)) * μ_B * B * (g_u m_J,u - g_l m_J,l)

def calc_shift_standard(lambda_nm, g_upper, mJ_upper, g_lower, mJ_lower, B_tesla):
    """Using standard formula with μ_B"""
    lambda_m = lambda_nm * 1e-9
    delta_E = mu_B * B_tesla * (g_upper * mJ_upper - g_lower * mJ_lower)
    delta_lambda_m = -(lambda_m**2 / (h * c)) * delta_E
    return delta_lambda_m * 1e9  # Convert to nm

# Test D1 transitions
print("D1 line (589.6 nm):")
for mJ_u, mJ_l in [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]:
    delta_mJ = mJ_u - mJ_l
    shift = calc_shift_standard(D1_wavelength, g_D1_upper, mJ_u, g_lower, mJ_l, B)
    print(f"  mJ_u={mJ_u:+.1f}, mJ_l={mJ_l:+.1f}, delta_mJ={delta_mJ:+.0f}, delta_lambda={shift:.6f} nm")

print("\nD2 line (589.0 nm):")
for mJ_u, mJ_l in [(-1.5, -0.5), (-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (1.5, 0.5)]:
    delta_mJ = mJ_u - mJ_l
    shift = calc_shift_standard(D2_wavelength, g_D2_upper, mJ_u, g_lower, mJ_l, B)
    print(f"  mJ_u={mJ_u:+.1f}, mJ_l={mJ_l:+.1f}, delta_mJ={delta_mJ:+.0f}, delta_lambda={shift:.6f} nm")

