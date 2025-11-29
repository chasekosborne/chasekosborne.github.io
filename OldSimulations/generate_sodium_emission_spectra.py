#!/usr/bin/env python3
"""
Generate SVG of sodium emission spectra in the same format as SodiumEmissionSpectra_f.svg.
Uses data from sodium_air_lines.csv and maps intensity to opacity.
"""

import csv
import math

# SVG parameters (matching Sodium format)
SVG_HEIGHT = 225.89355
# Set margins so axis goes from 380 nm to 780 nm tick positions
MARGIN_LEFT = 0  # 380 nm tick will be at x=0
# Calculate plot width based on wavelength range (400 nm range)
# Use a reasonable scale: ~1100 pixels for 400 nm range
PLOT_WIDTH = 1100
MARGIN_RIGHT = 0  # No padding - 780 nm tick is at the right edge
SVG_WIDTH = MARGIN_LEFT + PLOT_WIDTH + MARGIN_RIGHT

# Wavelength range (nm) - visible light spectrum
WAVELENGTH_MIN = 380
WAVELENGTH_MAX = 780

# Line parameters
LINE_WIDTH = 2
LINE_HEIGHT = 180
AXIS_Y = 180.39314  # Y position of the axis line

def wavelength_to_x(wavelength_nm):
    """Map wavelength to x position in SVG."""
    return MARGIN_LEFT + ((wavelength_nm - WAVELENGTH_MIN) / (WAVELENGTH_MAX - WAVELENGTH_MIN)) * PLOT_WIDTH

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

def read_sodium_data(csv_file):
    """Read sodium emission line data from CSV."""
    lines = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['Intensity'] or not row['Wavelength_Angstrom']:
                continue
            intensity = float(row['Intensity'])
            wavelength_angstrom = float(row['Wavelength_Angstrom'])
            wavelength_nm = wavelength_angstrom / 10.0  # Convert Angstrom to nm
            lines.append({
                'intensity': intensity,
                'wavelength_nm': wavelength_nm,
                'wavelength_angstrom': wavelength_angstrom
            })
    return lines

def normalize_intensities(lines):
    """Normalize intensities to 0-1 range for opacity."""
    if not lines:
        return lines
    
    max_intensity = max(line['intensity'] for line in lines)
    min_intensity = min(line['intensity'] for line in lines)
    
    # Normalize to 0.1-1.0 range (so even weakest lines are visible)
    for line in lines:
        if max_intensity > min_intensity:
            normalized = (line['intensity'] - min_intensity) / (max_intensity - min_intensity)
            line['opacity'] = 0.1 + 0.9 * normalized  # Scale to 0.1-1.0
        else:
            line['opacity'] = 1.0
    return lines

def generate_svg(csv_file, output_file):
    """Generate the complete SVG file."""
    # Read and process data
    lines = read_sodium_data(csv_file)
    lines = normalize_intensities(lines)
    
    # Filter lines within the wavelength range
    visible_lines = [line for line in lines if WAVELENGTH_MIN <= line['wavelength_nm'] <= WAVELENGTH_MAX]
    
    # Sort by wavelength
    visible_lines.sort(key=lambda x: x['wavelength_nm'])
    
    svg_lines = []
    svg_lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    svg_lines.append(f'<svg\n   width="{SVG_WIDTH}"\n   height="{SVG_HEIGHT}"\n   version="1.1"\n   '
                    f'xmlns="http://www.w3.org/2000/svg">')
    
    # Background (black)
    svg_lines.append(f'  <rect\n     width="{SVG_WIDTH}"\n     height="{SVG_HEIGHT}"\n     fill="#000000"\n     '
                    f'id="rect1"\n     x="0"\n     y="1.5099033e-14"\n     style="stroke-width:0.867743" />')
    
    # Draw emission lines
    for i, line in enumerate(visible_lines):
        x_center = wavelength_to_x(line['wavelength_nm'])
        x_left = x_center - LINE_WIDTH / 2
        color = wavelength_to_rgb_hex(line['wavelength_nm'])
        opacity = line['opacity']
        
        svg_lines.append(f'  <rect\n     x="{x_left:.4f}"\n     y="-0.10686089"\n     width="{LINE_WIDTH}"\n     '
                        f'height="{LINE_HEIGHT}"\n     fill="{color}"\n     opacity="1"\n     id="rect{i+2}"\n     '
                        f'style="opacity:{opacity:.3f}" />')
    
    # Draw axis line (horizontal line from 380 nm to 780 nm tick positions)
    x_min = wavelength_to_x(WAVELENGTH_MIN)
    x_max = wavelength_to_x(WAVELENGTH_MAX)
    svg_lines.append(f'  <line\n     x1="{x_min:.5f}"\n     y1="{AXIS_Y}"\n     x2="{x_max:.5f}"\n     '
                    f'y2="{AXIS_Y}"\n     stroke="#ffffff"\n     stroke-width="1.5"\n     id="axis_line" />')
    
    # Draw tick marks and labels
    # Major ticks every 50 nm (380, 430, 480, 530, 580, 630, 680, 730, 780)
    major_tick_interval = 50
    subtick_interval = 10  # Subticks every 10 nm
    
    # Draw subticks first (so they appear behind major ticks)
    subtick_wavelengths = []
    w = math.ceil(WAVELENGTH_MIN / subtick_interval) * subtick_interval
    while w <= WAVELENGTH_MAX:
        # Skip if it's a major tick position
        if w % major_tick_interval != 0:
            subtick_wavelengths.append(w)
        w += subtick_interval
    
    subtick_id = 200
    for wavelength in subtick_wavelengths:
        x = wavelength_to_x(wavelength)
        # Subtick mark (shorter than major ticks)
        svg_lines.append(f'  <line\n     x1="{x:.5f}"\n     y1="{AXIS_Y}"\n     x2="{x:.5f}"\n     y2="{AXIS_Y + 4}"\n     '
                        f'stroke="#ffffff"\n     stroke-width="1"\n     id="line{subtick_id}" />')
        subtick_id += 1
    
    # Draw major ticks and labels
    major_tick_wavelengths = []
    w = math.ceil(WAVELENGTH_MIN / major_tick_interval) * major_tick_interval
    while w <= WAVELENGTH_MAX:
        major_tick_wavelengths.append(w)
        w += major_tick_interval
    
    # Ensure boundary ticks are included
    if major_tick_wavelengths[0] != WAVELENGTH_MIN:
        major_tick_wavelengths.insert(0, WAVELENGTH_MIN)
    if major_tick_wavelengths[-1] != WAVELENGTH_MAX:
        major_tick_wavelengths.append(WAVELENGTH_MAX)
    
    for i, wavelength in enumerate(major_tick_wavelengths):
        x = wavelength_to_x(wavelength)
        # Major tick mark (longer than subticks)
        svg_lines.append(f'  <line\n     x1="{x:.5f}"\n     y1="{AXIS_Y}"\n     x2="{x:.5f}"\n     y2="{AXIS_Y + 8}"\n     '
                        f'stroke="#ffffff"\n     stroke-width="1.5"\n     id="line{i+120}" />')
        # Label (skip boundary ticks)
        if wavelength != WAVELENGTH_MIN and wavelength != WAVELENGTH_MAX:
            svg_lines.append(f'  <text\n     x="{x:.5f}"\n     y="{AXIS_Y + 20}"\n     fill="#ffffff"\n     font-size="12px"\n     '
                            f'font-family="Arial, sans-serif"\n     text-anchor="middle"\n     id="text{i+120}">{wavelength} nm</text>')
    
    # Axis label
    svg_lines.append(f'  <text\n     x="{SVG_WIDTH / 2}"\n     y="{SVG_HEIGHT - 8}"\n     fill="#ffffff"\n     '
                    f'font-size="14px"\n     font-family="Arial, sans-serif"\n     text-anchor="middle"\n     '
                    f'font-weight="bold"\n     id="text126">Wavelength (nm)</text>')
    
    svg_lines.append('</svg>')
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(svg_lines))
    
    print(f"Generated {output_file}")
    print(f"Plotted {len(visible_lines)} emission lines in the range {WAVELENGTH_MIN}-{WAVELENGTH_MAX} nm")
    if visible_lines:
        print(f"Intensity range: {min(l['intensity'] for l in visible_lines):.1f} - {max(l['intensity'] for l in visible_lines):.1f}")
        print(f"Opacity range: {min(l['opacity'] for l in visible_lines):.3f} - {max(l['opacity'] for l in visible_lines):.3f}")

if __name__ == '__main__':
    csv_file = 'sodium_air_lines.csv'
    output_file = '../image/spin-representation/SodiumEmissionSpectra_f.svg'
    generate_svg(csv_file, output_file)

