#!/usr/bin/env python3
"""
Custom Styling and Theme Demonstration
=======================================

Demonstrates advanced customization of Seaborn plots including:
- Custom color palettes
- Theme creation and application
- Color theory principles
- Accessibility considerations

Usage:
    python custom_styling.py
    python custom_styling.py --show-palettes
"""

import sys
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import apply_theme, stylize_plot, save_fig, create_color_palette


# Custom color palettes
BRAND_COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "accent": "#F18F01",
    "success": "#06A77D",
    "warning": "#F4B942",
    "danger": "#D62828"
}

ACCESSIBLE_PALETTE = [
    "#0173B2",  # Blue
    "#DE8F05",  # Orange
    "#029E73",  # Green
    "#CC78BC",  # Purple
    "#CA9161",  # Brown
    "#949494"   # Gray
]


def demonstrate_themes(output_dir: Path):
    """Demonstrate all Seaborn themes."""
    themes = ["darkgrid", "whitegrid", "dark", "white", "ticks"]
    
    # Sample data
    tips = sns.load_dataset("tips")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Seaborn Themes Comparison", fontsize=16, fontweight='bold', y=1.00)
    axes = axes.flatten()
    
    for idx, theme in enumerate(themes):
        ax = axes[idx]
        sns.set_style(theme)  # type: ignore[arg-type]
        sns.scatterplot(
            data=tips, x="total_bill", y="tip",
            hue="day", ax=ax, palette="Set2"
        )
        ax.set_title(f"Theme: {theme}", fontweight='bold')
        ax.legend(fontsize=8)
    
    # Hide extra subplot
    axes[-1].axis('off')
    
    plt.tight_layout()
    save_fig(output_dir / "theme_comparison.png")
    plt.close()
    print("  ✓ Created theme comparison")


def demonstrate_color_palettes(output_dir: Path):
    """Demonstrate different color palette types."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Sequential palette
    ax = axes[0]
    sequential = create_color_palette("sequential", 8)
    sns.palplot(sequential, size=1)
    ax.set_title("Sequential Palette (for ordered data)", fontweight='bold')
    
    # Diverging palette
    ax = axes[1]
    diverging = create_color_palette("diverging", 9)
    sns.palplot(diverging, size=1)
    ax.set_title("Diverging Palette (for data with meaningful center)", fontweight='bold')
    
    # Qualitative palette
    ax = axes[2]
    qualitative = create_color_palette("qualitative", 6)
    sns.palplot(qualitative, size=1)
    ax.set_title("Qualitative Palette (for categorical data)", fontweight='bold')
    
    plt.tight_layout()
    save_fig(output_dir / "palette_types.png")
    plt.close()
    print("  ✓ Created palette type comparison")


def demonstrate_custom_palette(output_dir: Path):
    """Demonstrate custom brand palette usage."""
    # Create sample data
    data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E', 'F'],
        'Values': [85, 72, 93, 65, 88, 79]
    })
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Using brand colors
    ax = axes[0]
    brand_palette = list(BRAND_COLORS.values())
    sns.barplot(
        data=data, x='Category', y='Values',
        palette=brand_palette, ax=ax
    )
    ax.set_title("Custom Brand Colors", fontweight='bold', fontsize=14)
    ax.set_ylabel("Performance Score")
    
    # Using accessible palette
    ax = axes[1]
    sns.barplot(
        data=data, x='Category', y='Values',
        palette=ACCESSIBLE_PALETTE, ax=ax
    )
    ax.set_title("Colorblind-Friendly Palette", fontweight='bold', fontsize=14)
    ax.set_ylabel("Performance Score")
    
    plt.tight_layout()
    save_fig(output_dir / "custom_palettes.png")
    plt.close()
    print("  ✓ Created custom palette examples")


def demonstrate_color_mapping(output_dir: Path):
    """Demonstrate categorical color mapping."""
    # Load data
    tips = sns.load_dataset("tips")
    
    # Custom color dictionary
    day_colors = {
        'Thur': BRAND_COLORS['primary'],
        'Fri': BRAND_COLORS['secondary'],
        'Sat': BRAND_COLORS['accent'],
        'Sun': BRAND_COLORS['success']
    }
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Default palette
    ax = axes[0]
    sns.boxplot(data=tips, x="day", y="total_bill", ax=ax)
    ax.set_title("Default Palette", fontweight='bold', fontsize=14)
    
    # Custom color mapping
    ax = axes[1]
    sns.boxplot(data=tips, x="day", y="total_bill", palette=day_colors, ax=ax)
    ax.set_title("Custom Color Mapping", fontweight='bold', fontsize=14)
    
    plt.tight_layout()
    save_fig(output_dir / "color_mapping.png")
    plt.close()
    print("  ✓ Created color mapping examples")


def demonstrate_gradient_palette(output_dir: Path):
    """Demonstrate custom gradient palettes."""
    # Create custom gradient
    colors = [BRAND_COLORS['primary'], BRAND_COLORS['accent'], BRAND_COLORS['secondary']]
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('brand_gradient', colors, N=n_bins)
    
    # Sample data
    data = pd.DataFrame({
        'x': range(20),
        'y': [i**1.5 + (i % 3) * 10 for i in range(20)],
        'category': [f'Cat{i%5}' for i in range(20)]
    })
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Heatmap with gradient
    ax = axes[0]
    matrix_data = [[i*j for i in range(10)] for j in range(10)]
    sns.heatmap(matrix_data, cmap=cmap, ax=ax, cbar_kws={'label': 'Value'})
    ax.set_title("Custom Gradient Heatmap", fontweight='bold', fontsize=14)
    
    # Scatter with gradient
    ax = axes[1]
    scatter = ax.scatter(
        data['x'], data['y'],
        c=data['y'], cmap=cmap,
        s=200, alpha=0.7, edgecolors='black', linewidth=1
    )
    plt.colorbar(scatter, ax=ax, label='Y Value')
    ax.set_title("Custom Gradient Scatter", fontweight='bold', fontsize=14)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    plt.tight_layout()
    save_fig(output_dir / "gradient_palettes.png")
    plt.close()
    print("  ✓ Created gradient palette examples")


def demonstrate_context_scaling(output_dir: Path):
    """Demonstrate context-based scaling."""
    contexts = ["paper", "notebook", "talk", "poster"]
    tips = sns.load_dataset("tips")
    
    fig = plt.figure(figsize=(16, 10))
    
    for idx, context in enumerate(contexts, 1):
        sns.set_context(context)  # type: ignore[arg-type]
        ax = fig.add_subplot(2, 2, idx)
        sns.scatterplot(data=tips, x="total_bill", y="tip", hue="time", ax=ax)
        ax.set_title(f"Context: {context}", fontweight='bold')
        ax.legend(fontsize='small')
    
    fig.suptitle("Seaborn Context Scaling", fontsize=18, fontweight='bold', y=0.995)
    plt.tight_layout()
    save_fig(output_dir / "context_scaling.png")
    plt.close()
    print("  ✓ Created context scaling examples")


def print_palette_info():
    """Print information about available palettes."""
    print("\n" + "="*60)
    print("🎨 AVAILABLE COLOR PALETTES")
    print("="*60 + "\n")
    
    print("Built-in Seaborn Palettes:")
    palettes = [
        "deep", "muted", "bright", "pastel", "dark", "colorblind",
        "Set1", "Set2", "Set3", "Paired", "viridis", "plasma"
    ]
    for palette in palettes:
        print(f"  • {palette}")
    
    print("\nBrand Colors (custom):")
    for name, color in BRAND_COLORS.items():
        print(f"  • {name}: {color}")
    
    print("\nAccessible Palette (colorblind-safe):")
    for i, color in enumerate(ACCESSIBLE_PALETTE, 1):
        print(f"  • Color {i}: {color}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Custom styling demonstrations")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "exports" / "examples",
        help="Output directory"
    )
    parser.add_argument(
        "--show-palettes",
        action="store_true",
        help="Display available palette information"
    )
    
    args = parser.parse_args()
    
    if args.show_palettes:
        print_palette_info()
        return
    
    print("\n" + "="*60)
    print("🎨 CUSTOM STYLING DEMONSTRATION")
    print("="*60 + "\n")
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Apply base theme
    apply_theme(style="whitegrid", context="notebook")
    
    print("Creating styling examples...\n")
    
    demonstrate_themes(args.output)
    demonstrate_color_palettes(args.output)
    demonstrate_custom_palette(args.output)
    demonstrate_color_mapping(args.output)
    demonstrate_gradient_palette(args.output)
    demonstrate_context_scaling(args.output)
    
    print("\n" + "="*60)
    print(f"✅ All examples saved to: {args.output}")
    print("="*60 + "\n")
    print("💡 Tip: Run with --show-palettes to see available color options")
    print("\n")


if __name__ == "__main__":
    main()
