#!/usr/bin/env python3
"""Generate Anomalous Zeeman Splitting diagram"""

import math

# Physical constants
mu_B = 9.274009994e-24
h = 6.62607015e-34
c = 2.99792458e8
B = 1.0

# Wavelengths
D2_wavelength = 589.0
D1_wavelength = 589.6

# g-factors
g_lower = 2.0023
g_D1_upper = 2.0 / 3.0
g_D2_upper = 4.0 / 3.0

def calculate_wavelength_shift(lambda_nm, g_upper, mJ_upper, g_lower, mJ_lower, B_tesla):
    lambda_m = lambda_nm * 1e-9
    delta_E = mu_B * B_tesla * (g_upper * mJ_upper - g_lower * mJ_lower)
    delta_lambda_m = -(lambda_m**2 / (h * c)) * delta_E
    return delta_lambda_m * 1e9

# SVG parameters
SVG_WIDTH = 1400
SVG_HEIGHT = 350
MARGIN_LEFT = 120
MARGIN_RIGHT = 120
MARGIN_TOP = 50
MARGIN_BOTTOM = 60

wavelength_min = 588.95
wavelength_max = 589.65
PLOT_WIDTH = SVG_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

def wavelength_to_x(wavelength):
    return MARGIN_LEFT + ((wavelength - wavelength_min) / (wavelength_max - wavelength_min)) * PLOT_WIDTH

def wavelength_to_rgb(wavelength_nm):
    """Convert wavelength in nm to RGB color (approximate visible spectrum)"""
    # Clamp to visible range
    wavelength_nm = max(380, min(780, wavelength_nm))
    
    if wavelength_nm < 440:
        r = -(wavelength_nm - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif wavelength_nm < 490:
        r = 0.0
        g = (wavelength_nm - 440) / (490 - 440)
        b = 1.0
    elif wavelength_nm < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength_nm - 510) / (510 - 490)
    elif wavelength_nm < 580:
        r = (wavelength_nm - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif wavelength_nm < 645:
        r = 1.0
        g = -(wavelength_nm - 645) / (645 - 580)
        b = 0.0
    else:
        r = 1.0
        g = 0.0
        b = 0.0
    
    # Adjust intensity for wavelengths near the edges
    if wavelength_nm < 420:
        factor = 0.3 + 0.7 * (wavelength_nm - 380) / (420 - 380)
    elif wavelength_nm > 700:
        factor = 0.3 + 0.7 * (780 - wavelength_nm) / (780 - 700)
    else:
        factor = 1.0
    
    r = int(255 * max(0, min(1, r * factor)))
    g = int(255 * max(0, min(1, g * factor)))
    b = int(255 * max(0, min(1, b * factor)))
    
    return f"rgb({r}, {g}, {b})"

def x_to_wavelength(x):
    """Convert x position back to wavelength"""
    return wavelength_min + ((x - MARGIN_LEFT) / PLOT_WIDTH) * (wavelength_max - wavelength_min)

LINE_WIDTH = 3.0
LINE_HEIGHT = 100
AXIS_Y = SVG_HEIGHT - MARGIN_BOTTOM
D2_Y_BASE = AXIS_Y - LINE_HEIGHT  # D2 directly on axis
D1_Y_BASE = AXIS_Y - LINE_HEIGHT  # D1 directly on axis (same y as D2)

svg_lines = []
svg_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
svg_lines.append(f'<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" xmlns="http://www.w3.org/2000/svg">')

# Black background
svg_lines.append(f'  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="black"/>')

# Axis line - white
axis_x1 = MARGIN_LEFT
axis_x2 = SVG_WIDTH - MARGIN_RIGHT
svg_lines.append(f'  <line x1="{axis_x1}" y1="{AXIS_Y}" x2="{axis_x2}" y2="{AXIS_Y}" '
                f'stroke="white" stroke-width="2"/>')

# Ticks - white, extend downward from axis
tick_spacing = 0.01
w = math.floor(wavelength_min / tick_spacing) * tick_spacing
major_tick_interval = 0.05
while w <= wavelength_max + 0.001:
    x = wavelength_to_x(w)
    is_major = abs(w - round(w / major_tick_interval) * major_tick_interval) < 0.001
    tick_len = 8 if is_major else 4
    svg_lines.append(f'  <line x1="{x:.3f}" y1="{AXIS_Y}" x2="{x:.3f}" y2="{AXIS_Y + tick_len}" '
                    f'stroke="white" stroke-width="1"/>')
    if is_major:
        svg_lines.append(f'  <text x="{x:.3f}" y="{AXIS_Y + 20}" fill="white" font-size="10" '
                        f'font-family="Arial, sans-serif" text-anchor="middle">{w:.2f}</text>')
    w += tick_spacing

# Axis label - white
svg_lines.append(f'  <text x="{SVG_WIDTH / 2}" y="{SVG_HEIGHT - 20}" fill="white" font-size="14" '
                f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">Wavelength (nm)</text>')

# D2 - 4 components in groups of 2
# Create 4 evenly spaced components around D2 wavelength
d2_center_x = wavelength_to_x(D2_wavelength)
d2_spacing = 15  # pixels between groups
d2_group_spacing = 5  # pixels within group

# Two groups of 2, centered around D2
d2_x_positions = [
    d2_center_x - d2_spacing - d2_group_spacing/2,
    d2_center_x - d2_spacing + d2_group_spacing/2,
    d2_center_x + d2_spacing - d2_group_spacing/2,
    d2_center_x + d2_spacing + d2_group_spacing/2,
]

for x_center in d2_x_positions:
    x_left = x_center - LINE_WIDTH / 2
    wavelength = x_to_wavelength(x_center)
    color = wavelength_to_rgb(wavelength)
    svg_lines.append(f'  <rect x="{x_left:.3f}" y="{D2_Y_BASE:.3f}" width="{LINE_WIDTH:.2f}" height="{LINE_HEIGHT}" '
                    f'fill="{color}" stroke="none"/>')

# D2 label
svg_lines.append(f'  <text x="{d2_center_x:.2f}" y="{D2_Y_BASE - 10}" fill="white" font-size="13" '
                f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">D2 (589.0 nm)</text>')

# D1 - 6 evenly spaced components
# Create 6 evenly spaced components around D1 wavelength
d1_center_x = wavelength_to_x(D1_wavelength)
d1_total_width = 60  # total width for 6 components
d1_spacing = d1_total_width / 5  # spacing between components

d1_x_positions = [
    d1_center_x - d1_total_width/2 + i * d1_spacing
    for i in range(6)
]

for x_center in d1_x_positions:
    x_left = x_center - LINE_WIDTH / 2
    wavelength = x_to_wavelength(x_center)
    color = wavelength_to_rgb(wavelength)
    svg_lines.append(f'  <rect x="{x_left:.3f}" y="{D1_Y_BASE:.3f}" width="{LINE_WIDTH:.2f}" height="{LINE_HEIGHT}" '
                    f'fill="{color}" stroke="none"/>')

# D1 label
svg_lines.append(f'  <text x="{d1_center_x:.2f}" y="{D1_Y_BASE - 10}" fill="white" font-size="13" '
                f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">D1 (589.6 nm)</text>')

svg_lines.append('</svg>')

print('\n'.join(svg_lines))

