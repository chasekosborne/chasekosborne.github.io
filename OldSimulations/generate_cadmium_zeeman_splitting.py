#!/usr/bin/env python3
"""
Generate SVG of normal Zeeman splitting for cadmium line at 643.8 nm.
Normal Zeeman effect: splits into three components labeled -1, 0, +1.
"""

import math

# Physical constants
mu_B = 9.274009994e-24  # J/T (Bohr magneton)
h = 6.62607015e-34  # J·s (Planck constant)
c = 2.99792458e8  # m/s (speed of light)
B = 1.0  # Tesla

# Central wavelength (from cadmium data: 6438.470 Angstrom = 643.847 nm)
CENTRAL_WAVELENGTH = 643.847  # nm

# For normal Zeeman effect, g = 1 for both states
g_upper = 1.0
g_lower = 1.0

# SVG parameters
SVG_WIDTH = 1200
SVG_HEIGHT = 210  # Reduced height (removed title space)
PLOT_TOP = 20
MARGIN_LEFT = 100
MARGIN_RIGHT = 100
PLOT_WIDTH = SVG_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Wavelength range (zoomed in around 643.8 nm)
# Show about ±0.05 nm around the central wavelength
WAVELENGTH_MIN = CENTRAL_WAVELENGTH - 0.05
WAVELENGTH_MAX = CENTRAL_WAVELENGTH + 0.05

# Line parameters
LINE_WIDTH = 4.0
LINE_HEIGHT = 100.0
LABEL_OFFSET_Y = 20

# Axis position (centered vertically in remaining space)
AXIS_Y = PLOT_TOP + LINE_HEIGHT + 40

def wavelength_to_x(wavelength):
    """Map wavelength to x position in SVG."""
    return MARGIN_LEFT + ((wavelength - WAVELENGTH_MIN) / (WAVELENGTH_MAX - WAVELENGTH_MIN)) * PLOT_WIDTH

def wavelength_to_rgb_hex(wavelength_nm):
    """Convert wavelength in nm to RGB hex color (approximate visible spectrum)"""
    # Clamp to visible range for color calculation
    wavelength_clamped = max(380, min(780, wavelength_nm))
    
    if wavelength_clamped < 440:
        r = -(wavelength_clamped - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif wavelength_clamped < 490:
        r = 0.0
        g = (wavelength_clamped - 440) / (490 - 440)
        b = 1.0
    elif wavelength_clamped < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength_clamped - 510) / (510 - 490)
    elif wavelength_clamped < 580:
        r = (wavelength_clamped - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif wavelength_clamped < 645:
        r = 1.0
        g = -(wavelength_clamped - 645) / (645 - 580)
        b = 0.0
    else:
        r = 1.0
        g = 0.0
        b = 0.0
    
    # Adjust intensity for wavelengths near the edges
    if wavelength_clamped < 420:
        factor = 0.3 + 0.7 * (wavelength_clamped - 380) / (420 - 380)
    elif wavelength_clamped > 700:
        factor = 0.3 + 0.7 * (780 - wavelength_clamped) / (780 - 700)
    else:
        factor = 1.0
    
    r = int(255 * max(0, min(1, r * factor)))
    g = int(255 * max(0, min(1, g * factor)))
    b = int(255 * max(0, min(1, b * factor)))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def calculate_wavelength_shift(delta_m, wavelength_nm, B_tesla):
    """
    Calculate wavelength shift for normal Zeeman effect.
    ΔE = μ_B * B * Δm (since g = 1 for normal Zeeman)
    Δλ = - (λ²/(hc)) * ΔE
    """
    delta_E = mu_B * B_tesla * delta_m
    lambda_m = wavelength_nm * 1e-9
    delta_lambda_m = -(lambda_m**2 / (h * c)) * delta_E
    delta_lambda_nm = delta_lambda_m * 1e9
    return delta_lambda_nm

def generate_svg():
    """Generate the complete SVG file."""
    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    svg_lines.append(f'<svg width="{SVG_WIDTH}" height="{SVG_HEIGHT}" version="1.1" '
                    f'xmlns="http://www.w3.org/2000/svg">')
    
    # Background
    svg_lines.append(f'  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="black"/>')
    
    # Calculate the three components
    components = []
    for delta_m in [-1, 0, 1]:
        shift = calculate_wavelength_shift(delta_m, CENTRAL_WAVELENGTH, B)
        wavelength = CENTRAL_WAVELENGTH + shift
        components.append({
            'delta_m': delta_m,
            'wavelength': wavelength,
            'shift': shift
        })
    
    # Sort by wavelength
    components_sorted = sorted(components, key=lambda x: x['wavelength'])
    
    # Draw tick marks first to determine axis boundaries
    # Show ticks every 0.01 nm, but only within the plot range
    tick_interval = 0.01
    tick_wavelengths = []
    w = math.ceil(WAVELENGTH_MIN / tick_interval) * tick_interval  # Start from first tick >= WAVELENGTH_MIN
    while w <= WAVELENGTH_MAX + 0.001:
        tick_wavelengths.append(round(w, 3))
        w += tick_interval
    
    # Filter ticks to only those within the plot area
    valid_ticks = []
    for wavelength in tick_wavelengths:
        x = wavelength_to_x(wavelength)
        if MARGIN_LEFT <= x <= (SVG_WIDTH - MARGIN_RIGHT):
            valid_ticks.append({'wavelength': wavelength, 'x': x})
    
    # Draw axis line from first tick to last tick
    if valid_ticks:
        first_tick_x = valid_ticks[0]['x']
        last_tick_x = valid_ticks[-1]['x']
        svg_lines.append(f'  <line x1="{first_tick_x:.3f}" y1="{AXIS_Y}" x2="{last_tick_x:.3f}" y2="{AXIS_Y}" '
                        f'stroke="white" stroke-width="1.5"/>')
    
    # Draw tick marks
    for tick in valid_ticks:
        wavelength = tick['wavelength']
        x = tick['x']
        # Tick mark (centered on axis)
        tick_length = 8 if abs(wavelength * 100 - round(wavelength * 100)) < 0.1 else 5
        svg_lines.append(f'  <line x1="{x:.3f}" y1="{AXIS_Y - tick_length/2}" x2="{x:.3f}" y2="{AXIS_Y + tick_length/2}" '
                        f'stroke="white" stroke-width="1"/>')
        # Label (every 0.02 nm to avoid crowding)
        if abs(wavelength * 100 - round(wavelength * 100)) < 0.1:
            svg_lines.append(f'  <text x="{x:.3f}" y="{AXIS_Y + 20}" fill="white" font-size="10" '
                            f'font-family="Arial, sans-serif" text-anchor="middle">{wavelength:.3f}</text>')
    
    # Axis label
    svg_lines.append(f'  <text x="{SVG_WIDTH / 2}" y="{SVG_HEIGHT - 10}" fill="white" font-size="14" '
                    f'font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">Wavelength (nm)</text>')
    
    # Draw the three Zeeman components (right on top of axis)
    y_top = AXIS_Y - LINE_HEIGHT  # Lines start at axis and go upward
    
    for comp in components_sorted:
        x_center = wavelength_to_x(comp['wavelength'])
        x_left = x_center - LINE_WIDTH / 2
        color = wavelength_to_rgb_hex(comp['wavelength'])  # Color based on actual wavelength
        
        # Draw line (positioned on axis)
        svg_lines.append(f'  <rect x="{x_left:.3f}" y="{y_top:.3f}" width="{LINE_WIDTH:.2f}" height="{LINE_HEIGHT:.2f}" '
                       f'fill="{color}"/>')
        
        # Draw label
        label_text = f"{comp['delta_m']:+d}" if comp['delta_m'] != 0 else "0"
        y_label = y_top - LABEL_OFFSET_Y
        svg_lines.append(f'  <text x="{x_center:.3f}" y="{y_label:.3f}" fill="white" '
                       f'font-size="14" font-family="Arial, sans-serif" text-anchor="middle" font-weight="bold">'
                       f'{label_text}</text>')
    
    svg_lines.append('</svg>')
    
    # Write to file
    output_file = '../image/spin-representation/CadmiumZeemanSplitting.svg'
    with open(output_file, 'w') as f:
        f.write('\n'.join(svg_lines))
    
    print(f"Generated {output_file}")
    print(f"Central wavelength: {CENTRAL_WAVELENGTH:.3f} nm")
    print("Zeeman components:")
    for comp in components_sorted:
        print(f"  delta_m = {comp['delta_m']:+d}: {comp['wavelength']:.6f} nm (shift: {comp['shift']*1000:.4f} pm)")

if __name__ == '__main__':
    generate_svg()

