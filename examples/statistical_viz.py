#!/usr/bin/env python3
"""
Statistical Visualization with Confidence Intervals
===================================================

Demonstrates statistical plotting with error bars, confidence intervals,
and significance testing.

Usage:
    python statistical_viz.py
    python statistical_viz.py --ci 95 --estimator median
"""

import sys
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import apply_theme, stylize_plot, save_fig, add_statistical_annotations


def create_comparison_plots(data: pd.DataFrame, output_dir: Path, ci: int = 95):
    """Create plots comparing different estimators."""
    estimators = {
        'Mean': 'mean',
        'Median': 'median',
        'Sum': 'sum'
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"Estimator Comparison (CI={ci}%)", fontsize=16, fontweight='bold')
    
    for ax, (name, estimator) in zip(axes, estimators.items()):
        sns.barplot(
            data=data,
            x='Category',
            y='Value',
            estimator=estimator,
            ci=ci,
            ax=ax,
            palette='Set2'
        )
        ax.set_title(f"{name} Estimator", fontweight='bold')
        ax.set_ylabel(f"{name} Value")
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_fig(output_dir / f"estimator_comparison_ci{ci}.png")
    plt.close()
    print(f"  ✓ Created estimator comparison (CI={ci}%)")


def create_errorbar_comparison(data: pd.DataFrame, output_dir: Path):
    """Compare different error bar types."""
    error_types = ['ci', 'sd', 'se']
    error_names = {
        'ci': 'Confidence Interval (95%)',
        'sd': 'Standard Deviation',
        'se': 'Standard Error'
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Error Bar Type Comparison", fontsize=16, fontweight='bold')
    
    for ax, error_type in zip(axes, error_types):
        if error_type == 'ci':
            sns.barplot(data=data, x='Category', y='Value', ci=95, ax=ax, palette='viridis')
        else:
            sns.barplot(data=data, x='Category', y='Value', errorbar=error_type, ax=ax, palette='viridis')
        
        ax.set_title(error_names[error_type], fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_fig(output_dir / "errorbar_comparison.png")
    plt.close()
    print("  ✓ Created error bar type comparison")


def create_bootstrap_visualization(data: pd.DataFrame, output_dir: Path, n_boot: int = 1000):
    """Visualize bootstrap confidence intervals."""
    categories = data['Category'].unique()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, category in enumerate(categories[:min(4, len(categories))]):
        ax = axes[idx]
        cat_data = data[data['Category'] == category]['Value']
        
        # Perform bootstrap
        bootstrap_means = []
        for _ in range(n_boot):
            sample = np.random.choice(cat_data, size=len(cat_data), replace=True)
            bootstrap_means.append(np.mean(sample))
        
        # Plot distribution
        ax.hist(bootstrap_means, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
        
        # Add confidence interval lines
        ci_lower = np.percentile(bootstrap_means, 2.5)
        ci_upper = np.percentile(bootstrap_means, 97.5)
        mean_val = np.mean(bootstrap_means)
        
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label='Mean')
        ax.axvline(ci_lower, color='green', linestyle=':', linewidth=2, label='95% CI')
        ax.axvline(ci_upper, color='green', linestyle=':', linewidth=2)
        
        ax.set_title(f"Bootstrap Distribution: {category}", fontweight='bold')
        ax.set_xlabel('Mean Value')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(alpha=0.3)
    
    fig.suptitle(f"Bootstrap Confidence Intervals (n={n_boot})", fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    save_fig(output_dir / "bootstrap_visualization.png")
    plt.close()
    print(f"  ✓ Created bootstrap visualization (n={n_boot})")


def create_regression_with_ci(output_dir: Path):
    """Create regression plot with confidence intervals."""
    # Load tips dataset
    tips = sns.load_dataset("tips")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Linear regression with CI
    ax = axes[0]
    sns.regplot(
        data=tips,
        x="total_bill",
        y="tip",
        ci=95,
        scatter_kws={'alpha': 0.5, 's': 50},
        line_kws={'color': 'red', 'linewidth': 2},
        ax=ax
    )
    ax.set_title("Linear Regression with 95% CI", fontweight='bold', fontsize=14)
    ax.set_xlabel("Total Bill ($)")
    ax.set_ylabel("Tip ($)")
    
    # LOWESS regression
    ax = axes[1]
    sns.regplot(
        data=tips,
        x="total_bill",
        y="tip",
        lowess=True,
        scatter_kws={'alpha': 0.5, 's': 50},
        line_kws={'color': 'green', 'linewidth': 2},
        ax=ax
    )
    ax.set_title("LOWESS Smoothing", fontweight='bold', fontsize=14)
    ax.set_xlabel("Total Bill ($)")
    ax.set_ylabel("Tip ($)")
    
    plt.tight_layout()
    save_fig(output_dir / "regression_with_ci.png")
    plt.close()
    print("  ✓ Created regression with confidence intervals")


def create_statistical_annotations_demo(data: pd.DataFrame, output_dir: Path):
    """Demonstrate statistical significance annotations."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar plot
    sns.barplot(
        data=data,
        x='Category',
        y='Value',
        ci=95,
        palette='Set1',
        ax=ax
    )
    
    # Add example significance annotation between categories A and B
    # In production, calculate actual p-values from your statistical test
    add_statistical_annotations(ax, x1=0, x2=1, y=data['Value'].max() * 1.1, p_value=0.03)
    
    ax.set_title("Statistical Significance Testing", fontweight='bold', fontsize=14)
    ax.set_ylabel("Value (with significance markers)")
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    save_fig(output_dir / "statistical_annotations.png")
    plt.close()
    print("  ✓ Created statistical annotations demo")


def create_custom_estimator_demo(data: pd.DataFrame, output_dir: Path):
    """Demonstrate custom estimator functions."""
    # Define custom estimators
    def iqr(x):
        """Interquartile range."""
        return np.percentile(x, 75) - np.percentile(x, 25)
    
    def percentile_90(x):
        """90th percentile."""
        return np.percentile(x, 90)
    
    custom_estimators = {
        'IQR': iqr,
        '90th Percentile': percentile_90,
        'Range': lambda x: np.max(x) - np.min(x)
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Custom Estimator Functions", fontsize=16, fontweight='bold')
    
    for ax, (name, func) in zip(axes, custom_estimators.items()):
        sns.barplot(
            data=data,
            x='Category',
            y='Value',
            estimator=func,
            ci=None,
            ax=ax,
            palette='rocket'
        )
        ax.set_title(name, fontweight='bold')
        ax.set_ylabel(f"{name} Value")
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_fig(output_dir / "custom_estimators.png")
    plt.close()
    print("  ✓ Created custom estimator examples")


def generate_sample_data(n_samples: int = 100) -> pd.DataFrame:
    """Generate sample data for demonstrations."""
    np.random.seed(42)
    
    categories = ['A', 'B', 'C', 'D']
    data = []
    
    for cat in categories:
        # Different distributions for each category
        if cat == 'A':
            values = np.random.normal(100, 15, n_samples)
        elif cat == 'B':
            values = np.random.normal(110, 20, n_samples)
        elif cat == 'C':
            values = np.random.normal(95, 10, n_samples)
        else:
            values = np.random.normal(105, 25, n_samples)
        
        for val in values:
            data.append({'Category': cat, 'Value': max(0, val)})
    
    return pd.DataFrame(data)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Statistical visualization demonstrations")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "exports" / "examples",
        help="Output directory"
    )
    parser.add_argument(
        "--ci",
        type=int,
        default=95,
        choices=[68, 90, 95, 99],
        help="Confidence interval percentage"
    )
    parser.add_argument(
        "--n-bootstrap",
        type=int,
        default=1000,
        help="Number of bootstrap iterations"
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=100,
        help="Number of samples per category"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📊 STATISTICAL VISUALIZATION DEMONSTRATION")
    print("="*60 + "\n")
    
    # Setup
    apply_theme(style="whitegrid", context="notebook", palette="deep")
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    print(f"Generating sample data (n={args.n_samples} per category)...\n")
    data = generate_sample_data(args.n_samples)
    
    print("Creating statistical visualizations...\n")
    
    create_comparison_plots(data, args.output, args.ci)
    create_errorbar_comparison(data, args.output)
    create_bootstrap_visualization(data, args.output, args.n_bootstrap)
    create_regression_with_ci(args.output)
    create_statistical_annotations_demo(data, args.output)
    create_custom_estimator_demo(data, args.output)
    
    print("\n" + "="*60)
    print(f"✅ All visualizations saved to: {args.output}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
