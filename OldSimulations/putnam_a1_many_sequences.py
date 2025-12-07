"""
Plot Many 2-Adic Valuation Sequences for Putnam 2025 A1

This script plots f(k) for many initial value pairs with large k values
to visualize the decreasing behavior and stabilization patterns.
"""

import numpy as np
import matplotlib.pyplot as plt
from math import gcd
import time


def v_2(x):
    """Compute the 2-adic valuation of x."""
    if x == 0:
        return float('inf')
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return v


def compute_sequence(m0, n0, max_k):
    """
    Compute the sequences m_k and n_k and f(k) from the recurrence relation.
    
    Returns:
        f_values: List of f(k) values
        k_values: List of k values
    """
    m_seq = [m0]
    n_seq = [n0]
    f_values = []
    
    # Compute initial f(0)
    diff = abs(m0 - n0)
    if diff == 0:
        f_values.append(0)
    else:
        v = v_2(diff)
        f_values.append(diff // (2 ** v))
    
    for k in range(1, max_k + 1):
        # Compute next terms
        num_m = 2 * m_seq[k-1] + 1
        num_n = 2 * n_seq[k-1] + 1
        
        # Reduce to lowest terms
        g = gcd(num_m, num_n)
        m_seq.append(num_m // g)
        n_seq.append(num_n // g)
        
        # Compute f(k)
        diff = abs(m_seq[k] - n_seq[k])
        if diff == 0:
            f_values.append(0)
            break
        else:
            v = v_2(diff)
            f_values.append(diff // (2 ** v))
        
        # Stop if values become too large (overflow protection)
        if m_seq[k] > 10**15 or n_seq[k] > 10**15:
            break
    
    k_values = list(range(len(f_values)))
    return f_values, k_values


def plot_many_sequences(m0_range, n0_range, max_k=500, max_sequences=100, 
                       save_path='putnam_2adic_many_sequences.png'):
    """
    Plot f(k) for many initial value pairs.
    
    Args:
        m0_range: Range of m0 values (e.g., range(1, 51))
        n0_range: Range of n0 values
        max_k: Maximum k to compute
        max_sequences: Maximum number of sequences to plot
        save_path: Path to save the figure
    """
    print(f"Computing sequences for up to {max_sequences} pairs with max_k={max_k}...")
    start_time = time.time()
    
    # Collect all sequences
    sequences = []
    pair_count = 0
    
    for m0 in m0_range:
        for n0 in n0_range:
            if m0 == n0:  # Must be distinct
                continue
            
            if pair_count >= max_sequences:
                break
            
            f_values, k_values = compute_sequence(m0, n0, max_k)
            sequences.append((m0, n0, f_values, k_values))
            pair_count += 1
            
            if pair_count % 50 == 0:
                elapsed = time.time() - start_time
                print(f"  Computed {pair_count} sequences ({elapsed:.1f}s)")
        
        if pair_count >= max_sequences:
            break
    
    elapsed = time.time() - start_time
    print(f"Completed {pair_count} sequences in {elapsed:.1f} seconds")
    print(f"Plotting...")
    
    # Create plot
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Use a color map for better visualization
    colors = plt.cm.viridis(np.linspace(0, 1, len(sequences)))
    
    max_k_plotted = 0
    
    for idx, (m0, n0, f_values, k_values) in enumerate(sequences):
        max_k_plotted = max(max_k_plotted, max(k_values) if k_values else 0)
        
        # Plot with transparency - use line plot for smoother appearance
        ax.plot(k_values, f_values, '-', color=colors[idx], 
                alpha=0.6, linewidth=1.2)
    
    ax.set_xlabel('$k$', fontsize=16)
    ax.set_ylabel('$f(k) = \\frac{|m_k - n_k|}{2^{\\nu_2(|m_k - n_k|)}}$', 
                  fontsize=16)
    ax.set_title(f'2-Adic Valuation Function $f(k)$ for {len(sequences)} Initial Value Pairs\n' +
                 f'Showing decreasing behavior up to $k={max_k_plotted}$',
                 fontsize=18, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0, max_k_plotted)
    
    # Add text box with statistics in top right corner
    stats_text = (f'Total sequences: {len(sequences)}\n' +
                 f'Initial pairs: $m_0 \\in [{min(m0_range)}, {max(m0_range)-1}]$, ' +
                 f'$n_0 \\in [{min(n0_range)}, {max(n0_range)-1}]$\n' +
                 f'Maximum $k$ computed: {max_k_plotted}')
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    
    plt.show()


if __name__ == "__main__":
    # Configuration
    MAX_K = 40  # Large k value
    M0_RANGE = range(1, 51)  # Many m0 values
    N0_RANGE = range(1, 51)  # Many n0 values
    MAX_SEQUENCES = 2450  # Number of sequences to plot
    
    print("=" * 70)
    print("2-Adic Valuation Function - Many Sequences Plot")
    print("=" * 70)
    print()
    
    plot_many_sequences(M0_RANGE, N0_RANGE, max_k=MAX_K, 
                       max_sequences=MAX_SEQUENCES,
                       save_path='putnam_2adic_many_sequences.svg')
    
    print("\n" + "=" * 70)
    print("Plotting complete!")
    print("=" * 70)

