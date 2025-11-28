#!/usr/bin/env python3
"""
Generate publication-quality SVG of anomalous Zeeman splitting of sodium D-lines.
Exact specifications: D1 at 589.000 nm, D2 at 589.600 nm, B = 1.0 T.
"""

import math
import csv

# Physical constants (exact values as specified)
mu_B = 9.274009994e-24  # J/T (Bohr magneton)
h = 6.62607015e-34  # J·s (Planck constant)
c = 2.99792458e8  # m/s (speed of light)
B = 1.0  # Tesla

# Central wavelengths (swapped as specified)
D1_wavelength = 589.000  # nm
D2_wavelength = 589.600  # nm

# Landé g-factors
g_lower = 2.0  # 3²S₁/₂
g_D1_upper = 2.0 / 3.0  # 3²P₁/₂
g_D2_upper = 4.0 / 3.0  # 3²P₃/₂

# SVG parameters
SVG_WIDTH = 1400
SVG_HEIGHT = 600
PLOT_TOP = 100
PLOT_BOTTOM = 450
MARGIN_LEFT = 120
MARGIN_RIGHT = 120
PLOT_WIDTH = SVG_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Wavelength range
WAVELENGTH_MIN = 588.5
WAVELENGTH_MAX = 590.5

# Line parameters
LINE_WIDTH = 3.0
LINE_HEIGHT = 200.0
LABEL_OFFSET_Y = 30

# Colors (yellow for ~589 nm)
D1_COLOR = "rgb(255, 255, 0)"  # Yellow
D2_COLOR = "rgb(255, 255, 0)"  # Yellow

def wavelength_to_x(wavelength):
    """Map wavelength to x position in SVG."""
    return MARGIN_LEFT + ((wavelength - WAVELENGTH_MIN) / (WAVELENGTH_MAX - WAVELENGTH_MIN)) * PLOT_WIDTH

def calculate_energy_shift(g_upper, mJ_upper, g_lower, mJ_lower, B_tesla):
    """Calculate energy shift: ΔE = μB * B * (g_upper*mJ_upper - g_lower*mJ_lower)"""
    delta_E = mu_B * B_tesla * (g_upper * mJ_upper - g_lower * mJ_lower)
    return delta_E  # in Joules

def energy_to_wavelength_shift(energy_J, wavelength_nm):
    """Convert energy shift to wavelength shift: Δλ ≈ - (λ² / (hc)) ΔE"""
    lambda_m = wavelength_nm * 1e-9
    delta_lambda_m = -(lambda_m**2 / (h * c)) * energy_J
    delta_lambda_nm = delta_lambda_m * 1e9
    return delta_lambda_nm

def get_allowed_transitions(J_upper, J_lower):
    """Get all allowed transitions with ΔmJ ∈ {-1, 0, +1}"""
    # mJ values for each J: mJ = -J, -J+1, ..., J-1, J
    # For half-integer J, mJ values are half-integers
    mJ_upper_list = []
    mJ_lower_list = []
    
    # Generate mJ values correctly for half-integer J
    if J_upper == 0.5:
        mJ_upper_list = [-0.5, 0.5]
    elif J_upper == 1.5:
        mJ_upper_list = [-1.5, -0.5, 0.5, 1.5]
    
    if J_lower == 0.5:
        mJ_lower_list = [-0.5, 0.5]
    
    transitions = []
    for mJ_u in mJ_upper_list:
        for mJ_l in mJ_lower_list:
            delta_mJ = mJ_u - mJ_l
            if delta_mJ in [-1, 0, 1]:
                transitions.append((mJ_u, mJ_l, int(delta_mJ)))
    
    return transitions

def generate_svg():
    """Generate the complete SVG file."""
    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg_lines.append(f'<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" xmlns="http://www.w3.org/2000/svg">')
    
    # Background
    svg_lines.append(f'  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="black"/>')
    
    # Title
    svg_lines.append(f'  <text x="{SVG_WIDTH / 2}" y="35" fill="white" font-size="20" '
                    f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">'
                    f'Anomalous Zeeman Splitting of Sodium D-Lines</text>')
    
    # Draw axis line
    axis_y = PLOT_BOTTOM + 20
    svg_lines.append(f'  <line x1="{MARGIN_LEFT}" y1="{axis_y}" x2="{SVG_WIDTH - MARGIN_RIGHT}" y2="{axis_y}" '
                    f'stroke="white" stroke-width="1.5"/>')
    
    # Draw tick marks every 0.2 nm
    tick_wavelengths = []
    w = WAVELENGTH_MIN
    while w <= WAVELENGTH_MAX + 0.01:  # Small epsilon for floating point
        tick_wavelengths.append(round(w, 1))
        w += 0.2
    
    for wavelength in tick_wavelengths:
        x = wavelength_to_x(wavelength)
        # Tick mark
        tick_length = 8 if abs(wavelength - round(wavelength)) < 0.01 else 5  # Longer for whole numbers
        svg_lines.append(f'  <line x1="{x:.2f}" y1="{axis_y}" x2="{x:.2f}" y2="{axis_y + tick_length}" '
                        f'stroke="white" stroke-width="1"/>')
        # Label (only for whole and half numbers to avoid crowding)
        if abs(wavelength - round(wavelength)) < 0.01 or abs(wavelength - round(wavelength) - 0.5) < 0.01:
            svg_lines.append(f'  <text x="{x:.2f}" y="{axis_y + 22}" fill="white" font-size="10" '
                            f'font-family="Arial, sans-serif" text-anchor="middle">{wavelength:.1f}</text>')
    
    # Axis label
    svg_lines.append(f'  <text x="{SVG_WIDTH / 2}" y="{SVG_HEIGHT - 15}" fill="white" font-size="14" '
                    f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">Wavelength (nm)</text>')
    
    # Calculate and plot D1 transitions (J_upper = 1/2, J_lower = 1/2)
    d1_transitions = get_allowed_transitions(0.5, 0.5)
    d1_components = []
    
    for mJ_u, mJ_l, delta_mJ in d1_transitions:
        delta_E = calculate_energy_shift(g_D1_upper, mJ_u, g_lower, mJ_l, B)
        delta_lambda = energy_to_wavelength_shift(delta_E, D1_wavelength)
        shifted_wavelength = D1_wavelength + delta_lambda
        d1_components.append({
            'mJ_upper': mJ_u,
            'mJ_lower': mJ_l,
            'delta_mJ': delta_mJ,
            'wavelength': shifted_wavelength,
            'delta_lambda': delta_lambda
        })
    
    # Calculate and plot D2 transitions (J_upper = 3/2, J_lower = 1/2)
    d2_transitions = get_allowed_transitions(1.5, 0.5)
    d2_components = []
    
    for mJ_u, mJ_l, delta_mJ in d2_transitions:
        delta_E = calculate_energy_shift(g_D2_upper, mJ_u, g_lower, mJ_l, B)
        delta_lambda = energy_to_wavelength_shift(delta_E, D2_wavelength)
        shifted_wavelength = D2_wavelength + delta_lambda
        d2_components.append({
            'mJ_upper': mJ_u,
            'mJ_lower': mJ_l,
            'delta_mJ': delta_mJ,
            'wavelength': shifted_wavelength,
            'delta_lambda': delta_lambda
        })
    
    # Draw D1 components
    d1_y_base = PLOT_TOP + 50
    d1_x_center = wavelength_to_x(D1_wavelength)
    
    # D1 header
    svg_lines.append(f'  <text x="{d1_x_center:.2f}" y="{PLOT_TOP + 20}" fill="white" font-size="16" '
                    f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">D1</text>')
    svg_lines.append(f'  <line x1="{d1_x_center:.2f}" y1="{PLOT_TOP + 25}" x2="{d1_x_center:.2f}" y2="{PLOT_TOP + 30}" '
                    f'stroke="white" stroke-width="1"/>')
    
    # Sort D1 components by wavelength for plotting
    d1_components_sorted = sorted(d1_components, key=lambda x: x['wavelength'])
    
    for comp in d1_components_sorted:
        x_center = wavelength_to_x(comp['wavelength'])
        x_left = x_center - LINE_WIDTH / 2
        y_top = d1_y_base
        
        # Draw line
        svg_lines.append(f'  <rect x="{x_left:.2f}" y="{y_top:.2f}" width="{LINE_WIDTH:.2f}" height="{LINE_HEIGHT:.2f}" '
                       f'fill="{D1_COLOR}" data-wavelength="{comp["wavelength"]:.6f}" data-delta-mj="{comp["delta_mJ"]}"/>')
        
        # Draw label
        label_text = f"{comp['delta_mJ']:+d}" if comp['delta_mJ'] != 0 else "0"
        y_label = y_top - LABEL_OFFSET_Y
        svg_lines.append(f'  <text x="{x_center:.2f}" y="{y_label:.2f}" fill="white" '
                       f'font-size="12" font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">'
                       f'{label_text}</text>')
    
    # Draw D2 components
    d2_y_base = PLOT_TOP + 50
    d2_x_center = wavelength_to_x(D2_wavelength)
    
    # D2 header
    svg_lines.append(f'  <text x="{d2_x_center:.2f}" y="{PLOT_TOP + 20}" fill="white" font-size="16" '
                    f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">D2</text>')
    svg_lines.append(f'  <line x1="{d2_x_center:.2f}" y1="{PLOT_TOP + 25}" x2="{d2_x_center:.2f}" y2="{PLOT_TOP + 30}" '
                    f'stroke="white" stroke-width="1"/>')
    
    # Sort D2 components by wavelength for plotting
    d2_components_sorted = sorted(d2_components, key=lambda x: x['wavelength'])
    
    for comp in d2_components_sorted:
        x_center = wavelength_to_x(comp['wavelength'])
        x_left = x_center - LINE_WIDTH / 2
        y_top = d2_y_base
        
        # Draw line
        svg_lines.append(f'  <rect x="{x_left:.2f}" y="{y_top:.2f}" width="{LINE_WIDTH:.2f}" height="{LINE_HEIGHT:.2f}" '
                       f'fill="{D2_COLOR}" data-wavelength="{comp["wavelength"]:.6f}" data-delta-mj="{comp["delta_mJ"]}"/>')
        
        # Draw label
        label_text = f"{comp['delta_mJ']:+d}" if comp['delta_mJ'] != 0 else "0"
        y_label = y_top - LABEL_OFFSET_Y
        svg_lines.append(f'  <text x="{x_center:.2f}" y="{y_label:.2f}" fill="white" '
                       f'font-size="12" font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">'
                       f'{label_text}</text>')
    
    # Legend
    legend_x = SVG_WIDTH - 200
    legend_y = 100
    svg_lines.append(f'  <rect x="{legend_x - 10}" y="{legend_y - 10}" width="180" height="80" '
                    f'fill="none" stroke="white" stroke-width="1" opacity="0.5"/>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 15}" fill="white" font-size="11" '
                    f'font-family="Arial, sans-serif">B = 1.0 T</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 35}" fill="white" font-size="11" '
                    f'font-family="Arial, sans-serif">Landé g:</text>')
    svg_lines.append(f'  <text x="{legend_x}" y="{legend_y + 55}" fill="white" font-size="11" '
                    f'font-family="Arial, sans-serif">3/2-&gt;4/3, 1/2-&gt;2/3, lower=2.0</text>')
    
    svg_lines.append('</svg>')
    
    return '\n'.join(svg_lines), d1_components, d2_components

def generate_data_table(d1_components, d2_components):
    """Generate CSV data table of all components."""
    rows = []
    rows.append(['component_id', 'parent_line', 'delta_mJ', 'wavelength_nm', 'mJ_upper', 'mJ_lower'])
    
    # D1 components
    for i, comp in enumerate(sorted(d1_components, key=lambda x: x['wavelength']), 1):
        rows.append([
            f'D1_{i}',
            'D1',
            comp['delta_mJ'],
            f"{comp['wavelength']:.6f}",
            f"{comp['mJ_upper']:.1f}",
            f"{comp['mJ_lower']:.1f}"
        ])
    
    # D2 components
    for i, comp in enumerate(sorted(d2_components, key=lambda x: x['wavelength']), 1):
        rows.append([
            f'D2_{i}',
            'D2',
            comp['delta_mJ'],
            f"{comp['wavelength']:.6f}",
            f"{comp['mJ_upper']:.1f}",
            f"{comp['mJ_lower']:.1f}"
        ])
    
    return rows

if __name__ == "__main__":
    svg_content, d1_comps, d2_comps = generate_svg()
    print(svg_content)
    
    # Print data table to stderr or as comment
    print("\n<!-- Component Data Table -->", file=__import__('sys').stderr)
    data_table = generate_data_table(d1_comps, d2_comps)
    for row in data_table:
        print(",".join(str(x) for x in row), file=__import__('sys').stderr)

