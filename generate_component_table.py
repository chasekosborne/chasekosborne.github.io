#!/usr/bin/env python3
"""Generate component data table from the Zeeman splitting calculations."""
from generate_anomalous_zeeman_final import generate_svg, generate_data_table

svg_content, d1_comps, d2_comps = generate_svg()
data_table = generate_data_table(d1_comps, d2_comps)

print("Component Data Table:")
print("=" * 80)
for row in data_table:
    print(",".join(str(x) for x in row))

