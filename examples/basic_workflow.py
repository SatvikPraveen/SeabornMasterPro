#!/usr/bin/env python3
"""
Basic Seaborn Visualization Workflow
=====================================

Demonstrates a complete end-to-end workflow for creating visualizations with Seaborn.
This script covers data loading, basic plots, customization, and saving.

Usage:
    python basic_workflow.py
    python basic_workflow.py --dataset sales --output ./my_plots
"""

import sys
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import apply_theme, stylize_plot, save_fig


def load_data(dataset_name: str = "sales_data") -> pd.DataFrame:
    """
    Load dataset from the datasets folder.
    
    Args:
        dataset_name: Name of the dataset (without .csv extension)
        
    Returns:
        DataFrame with loaded data
    """
    data_path = Path(__file__).parent.parent / "datasets" / f"{dataset_name}.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {dataset_name}.csv: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def create_distribution_plot(df: pd.DataFrame, column: str, output_dir: Path) -> None:
    """Create a distribution plot with histogram and KDE."""
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x=column, kde=True, bins=30)
    
    stylize_plot(
        title=f"Distribution of {column}",
        xlabel=column,
        ylabel="Frequency"
    )
    
    save_fig(output_dir / f"{column.lower().replace(' ', '_')}_distribution.png")
    plt.close()
    print(f"  ✓ Created distribution plot for {column}")


def create_scatter_plot(df: pd.DataFrame, x: str, y: str, hue: str, output_dir: Path) -> None:
    """Create a scatter plot with categorical coloring."""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, s=100, alpha=0.7)
    
    stylize_plot(
        title=f"{y} vs {x}",
        xlabel=x,
        ylabel=y
    )
    
    plt.legend(title=hue, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    save_fig(output_dir / f"{y.lower().replace(' ', '_')}_vs_{x.lower().replace(' ', '_')}.png")
    plt.close()
    print(f"  ✓ Created scatter plot: {y} vs {x}")


def create_categorical_plot(df: pd.DataFrame, x: str, y: str, output_dir: Path) -> None:
    """Create a categorical bar plot."""
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x=x, y=y, palette="viridis", ci=95)
    
    stylize_plot(
        title=f"Average {y} by {x}",
        xlabel=x,
        ylabel=f"Average {y}"
    )
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    save_fig(output_dir / f"{y.lower().replace(' ', '_')}_by_{x.lower().replace(' ', '_')}.png")
    plt.close()
    print(f"  ✓ Created bar plot: {y} by {x}")


def create_correlation_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    """Create a correlation heatmap for numeric columns."""
    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) < 2:
        print("  ⚠ Skipping heatmap: not enough numeric columns")
        return
    
    plt.figure(figsize=(10, 8))
    correlation_matrix = df[numeric_cols].corr()
    
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8}
    )
    
    plt.title("Correlation Heatmap", fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    save_fig(output_dir / "correlation_heatmap.png")
    plt.close()
    print("  ✓ Created correlation heatmap")


def main():
    """Main workflow execution."""
    parser = argparse.ArgumentParser(description="Basic Seaborn visualization workflow")
    parser.add_argument(
        "--dataset",
        type=str,
        default="sales_data",
        help="Dataset name (without .csv extension)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "exports" / "examples",
        help="Output directory for plots"
    )
    
    args = parser.parse_args()
    
    # Setup
    print("\n" + "="*60)
    print("🎨 BASIC SEABORN WORKFLOW")
    print("="*60 + "\n")
    
    # Apply theme
    apply_theme(style="whitegrid", context="notebook", palette="husl")
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {args.output}\n")
    
    # Load data
    df = load_data(args.dataset)
    print(f"\nDataset columns: {list(df.columns)}\n")
    
    # Create visualizations based on dataset
    print("Creating visualizations...\n")
    
    # Example: sales_data specific plots
    if args.dataset == "sales_data":
        create_distribution_plot(df, "Revenue", args.output)
        create_scatter_plot(df, "Quantity", "Revenue", "Product Category", args.output)
        create_categorical_plot(df, "Product Category", "Revenue", args.output)
        create_correlation_heatmap(df, args.output)
    
    # Generic approach for any dataset
    else:
        # Distribution for first numeric column
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            create_distribution_plot(df, numeric_cols[0], args.output)
        
        # Correlation heatmap
        create_correlation_heatmap(df, args.output)
    
    print("\n" + "="*60)
    print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
