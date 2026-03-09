#!/usr/bin/env python3
"""
Publication-Ready Figure Generation
====================================

Creates publication-quality figures with proper sizing, DPI, and formatting
suitable for journals, presentations, and reports.

Usage:
    python publication_figures.py
    python publication_figures.py --size journal --dpi 300 --formats pdf svg
"""

import sys
from pathlib import Path
import argparse
from typing import List, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import apply_theme, stylize_plot, save_publication_figure


# Publication size presets (width, height) in inches
FIGURE_SIZES = {
    'journal_single': (3.5, 2.625),      # Single column for most journals
    'journal_double': (7.0, 5.25),       # Double column for most journals
    'presentation': (10, 7.5),            # 4:3 aspect ratio
    'presentation_wide': (12, 6.75),      # 16:9 aspect ratio
    'poster': (16, 12),                   # Large poster format
    'nature': (89/25.4, 89/25.4),        # Nature single column (89mm)
    'science': (55/25.4, 55/25.4),       # Science single column (55mm)
}

# Font size presets for different contexts
FONT_PRESETS = {
    'journal': {'title': 10, 'label': 9, 'tick': 8, 'legend': 8},
    'presentation': {'title': 16, 'label': 14, 'tick': 12, 'legend': 12},
    'poster': {'title': 24, 'label': 20, 'tick': 18, 'legend': 18},
}


def configure_for_publication(size_preset: str = 'journal_double', 
                              font_preset: str = 'journal',
                              dpi: int = 300):
    """
    Configure matplotlib for publication-quality output.
    
    Args:
        size_preset: Figure size preset
        font_preset: Font size preset
        dpi: Resolution in dots per inch
    """
    fonts = FONT_PRESETS.get(font_preset, FONT_PRESETS['journal'])
    
    rcParams.update({
        'figure.dpi': dpi,
        'savefig.dpi': dpi,
        'font.size': fonts['label'],
        'axes.titlesize': fonts['title'],
        'axes.labelsize': fonts['label'],
        'xtick.labelsize': fonts['tick'],
        'ytick.labelsize': fonts['tick'],
        'legend.fontsize': fonts['legend'],
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'axes.linewidth': 0.8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'lines.linewidth': 1.5,
        'patch.linewidth': 0.5,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
    })


def create_journal_scatter(data: pd.DataFrame, output_dir: Path, 
                           size_preset: str, formats: List[str]):
    """Create publication-ready scatter plot."""
    fig_width, fig_height = FIGURE_SIZES[size_preset]
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Create scatter plot
    scatter = ax.scatter(
        data['total_bill'], 
        data['tip'],
        c=data['size'],
        s=30,
        alpha=0.6,
        cmap='viridis',
        edgecolors='black',
        linewidth=0.3
    )
    
    # Add colorbar with proper sizing
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Party Size', rotation=270, labelpad=15)
    
    # Labels and title
    ax.set_xlabel('Total Bill ($)')
    ax.set_ylabel('Tip ($)')
    ax.set_title('Tip Amount vs Total Bill', pad=10)
    
    # Add gridlines
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    filename = f"scatter_plot_{size_preset}"
    save_publication_figure(fig, output_dir / filename, formats)
    plt.close()
    
    print(f"  ✓ Created scatter plot ({size_preset})")


def create_journal_multiplot(data: pd.DataFrame, output_dir: Path,
                             size_preset: str, formats: List[str]):
    """Create multi-panel publication figure."""
    fig_width, fig_height = FIGURE_SIZES[size_preset]
    
    fig, axes = plt.subplots(2, 2, figsize=(fig_width, fig_height))
    
    # Panel A: Distribution
    ax = axes[0, 0]
    sns.histplot(data=data, x='total_bill', kde=True, ax=ax, color='steelblue')
    ax.set_xlabel('Total Bill ($)')
    ax.set_ylabel('Frequency')
    ax.text(0.05, 0.95, 'A', transform=ax.transAxes, fontsize=14, 
            fontweight='bold', va='top')
    
    # Panel B: Box plot
    ax = axes[0, 1]
    sns.boxplot(data=data, x='day', y='total_bill', ax=ax, palette='Set2')
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Total Bill ($)')
    ax.tick_params(axis='x', rotation=45)
    ax.text(0.05, 0.95, 'B', transform=ax.transAxes, fontsize=14,
            fontweight='bold', va='top')
    
    # Panel C: Violin plot
    ax = axes[1, 0]
    sns.violinplot(data=data, x='time', y='tip', ax=ax, palette='muted')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Tip ($)')
    ax.text(0.05, 0.95, 'C', transform=ax.transAxes, fontsize=14,
            fontweight='bold', va='top')
    
    # Panel D: Regression
    ax = axes[1, 1]
    sns.regplot(data=data, x='total_bill', y='tip', ax=ax,
                scatter_kws={'s': 20, 'alpha': 0.5},
                line_kws={'color': 'red', 'linewidth': 1.5})
    ax.set_xlabel('Total Bill ($)')
    ax.set_ylabel('Tip ($)')
    ax.text(0.05, 0.95, 'D', transform=ax.transAxes, fontsize=14,
            fontweight='bold', va='top')
    
    plt.tight_layout()
    
    filename = f"multiplot_{size_preset}"
    save_publication_figure(fig, output_dir / filename, formats)
    plt.close()
    
    print(f"  ✓ Created multi-panel plot ({size_preset})")


def create_journal_barplot(data: pd.DataFrame, output_dir: Path,
                           size_preset: str, formats: List[str]):
    """Create publication-ready bar plot with error bars."""
    fig_width, fig_height = FIGURE_SIZES[size_preset]
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Create bar plot
    sns.barplot(
        data=data,
        x='day',
        y='total_bill',
        ci=95,
        ax=ax,
        palette='colorblind',
        edgecolor='black',
        linewidth=0.5
    )
    
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Average Total Bill ($)')
    ax.set_title('Daily Revenue Analysis', pad=10)
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', padding=3, fontsize=7)  # type: ignore[arg-type]
    
    plt.tight_layout()
    
    filename = f"barplot_{size_preset}"
    save_publication_figure(fig, output_dir / filename, formats)
    plt.close()
    
    print(f"  ✓ Created bar plot ({size_preset})")


def create_high_contrast_plot(data: pd.DataFrame, output_dir: Path,
                              size_preset: str, formats: List[str]):
    """Create high-contrast plot suitable for black & white printing."""
    fig_width, fig_height = FIGURE_SIZES[size_preset]
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Use distinct markers and line styles instead of colors
    days = data['day'].unique()
    markers = ['o', 's', '^', 'D']
    linestyles = ['-', '--', '-.', ':']
    
    for idx, day in enumerate(days):
        day_data = data[data['day'] == day]
        ax.scatter(
            day_data['total_bill'],
            day_data['tip'],
            marker=markers[idx % len(markers)],
            s=50,
            label=day,
            color='black',
            alpha=0.6
        )
    
    ax.set_xlabel('Total Bill ($)')
    ax.set_ylabel('Tip ($)')
    ax.set_title('Grayscale-Friendly Plot', pad=10)
    ax.legend(frameon=True, fancybox=False, shadow=False)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    
    filename = f"grayscale_{size_preset}"
    save_publication_figure(fig, output_dir / filename, formats)
    plt.close()
    
    print(f"  ✓ Created grayscale plot ({size_preset})")


def create_heatmap_publication(data: pd.DataFrame, output_dir: Path,
                               size_preset: str, formats: List[str]):
    """Create publication-ready correlation heatmap."""
    fig_width, fig_height = FIGURE_SIZES[size_preset]
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Calculate correlation
    numeric_cols = ['total_bill', 'tip', 'size']
    corr = data[numeric_cols].corr()  # type: ignore[call-arg]
    
    # Create heatmap
    sns.heatmap(
        corr,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        square=True,
        linewidths=0.5,
        linecolor='black',
        cbar_kws={'shrink': 0.8, 'label': 'Correlation'},
        ax=ax
    )
    
    ax.set_title('Correlation Matrix', pad=10)
    
    plt.tight_layout()
    
    filename = f"heatmap_{size_preset}"
    save_publication_figure(fig, output_dir / filename, formats)
    plt.close()
    
    print(f"  ✓ Created heatmap ({size_preset})")


def create_size_comparison_grid(data: pd.DataFrame, output_dir: Path):
    """Create a grid showing different publication sizes."""
    print("\n  Creating size comparison grid...")
    
    sizes_to_compare = ['journal_single', 'journal_double', 'presentation']
    
    for size_name in sizes_to_compare:
        w, h = FIGURE_SIZES[size_name]
        fig, ax = plt.subplots(figsize=(w, h))
        
        sns.scatterplot(data=data, x='total_bill', y='tip', 
                       hue='time', ax=ax, s=50, alpha=0.7)
        ax.set_xlabel('Total Bill ($)')
        ax.set_ylabel('Tip ($)')
        ax.set_title(f'{size_name.replace("_", " ").title()}', pad=8)
        ax.legend(fontsize='small')
        
        plt.tight_layout()
        save_publication_figure(fig, output_dir / f"demo_{size_name}", ['png'])
        plt.close()
        
        print(f"    ✓ {size_name}: {w}\" × {h}\"")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Publication-ready figure generation")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "exports" / "publication",
        help="Output directory"
    )
    parser.add_argument(
        "--size",
        type=str,
        default="journal_double",
        choices=list(FIGURE_SIZES.keys()),
        help="Figure size preset"
    )
    parser.add_argument(
        "--font",
        type=str,
        default="journal",
        choices=list(FONT_PRESETS.keys()),
        help="Font size preset"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        choices=[150, 300, 600, 1200],
        help="Resolution (DPI)"
    )
    parser.add_argument(
        "--formats",
        type=str,
        nargs='+',
        default=['png', 'pdf'],
        choices=['png', 'pdf', 'svg', 'eps'],
        help="Output formats"
    )
    parser.add_argument(
        "--show-sizes",
        action='store_true',
        help="Create comparison of all sizes"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📄 PUBLICATION-READY FIGURE GENERATION")
    print("="*60 + "\n")
    
    # Configure for publication
    configure_for_publication(args.size, args.font, args.dpi)
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Load sample data
    print("Loading data...")
    tips = sns.load_dataset("tips")
    print(f"✅ Loaded tips dataset: {len(tips)} rows\n")
    
    print(f"Settings:")
    print(f"  • Size: {args.size} {FIGURE_SIZES[args.size]}")
    print(f"  • Font: {args.font}")
    print(f"  • DPI: {args.dpi}")
    print(f"  • Formats: {', '.join(args.formats)}\n")
    
    # Create figures
    print("Creating publication figures...\n")
    
    create_journal_scatter(tips, args.output, args.size, args.formats)
    create_journal_multiplot(tips, args.output, args.size, args.formats)
    create_journal_barplot(tips, args.output, args.size, args.formats)
    create_high_contrast_plot(tips, args.output, args.size, args.formats)
    create_heatmap_publication(tips, args.output, args.size, args.formats)
    
    if args.show_sizes:
        create_size_comparison_grid(tips, args.output)
    
    print("\n" + "="*60)
    print(f"✅ Publication figures saved to: {args.output}")
    print(f"   Formats: {', '.join(args.formats)}")
    print(f"   Resolution: {args.dpi} DPI")
    print("="*60 + "\n")
    print("💡 Pro tips:")
    print("  • Use --show-sizes to see all size presets")
    print("  • PDF/SVG formats are vector-based (infinitely scalable)")
    print("  • Use 300 DPI for print, 150 DPI for screen")
    print("\n")


if __name__ == "__main__":
    main()
