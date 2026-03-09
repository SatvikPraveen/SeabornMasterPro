#!/usr/bin/env python3
"""
Production-Ready Multi-Plot Dashboard
======================================

Creates a comprehensive multi-panel dashboard suitable for production use.
Demonstrates best practices for layout, styling, and exporting.

Usage:
    python production_dashboard.py
    python production_dashboard.py --dataset ecommerce_data --format pdf
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import apply_theme, stylize_plot, save_publication_figure


class DashboardGenerator:
    """Generates production-ready visualization dashboards."""
    
    def __init__(self, data: pd.DataFrame, output_dir: Path):
        """
        Initialize dashboard generator.
        
        Args:
            data: DataFrame to visualize
            output_dir: Directory for saving outputs
        """
        self.data = data
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_header(self, fig, title: str):
        """Add dashboard header with title and metadata."""
        fig.text(
            0.5, 0.98, title,
            ha='center', va='top',
            fontsize=20, fontweight='bold'
        )
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fig.text(
            0.99, 0.01, f"Generated: {timestamp}",
            ha='right', va='bottom',
            fontsize=8, style='italic', alpha=0.7
        )
        
    def create_kpi_summary(self, ax, metrics: dict):
        """Create KPI summary panel."""
        ax.axis('off')
        
        y_pos = 0.9
        for label, value in metrics.items():
            ax.text(
                0.1, y_pos, f"{label}:",
                fontsize=12, fontweight='bold',
                transform=ax.transAxes
            )
            ax.text(
                0.7, y_pos, str(value),
                fontsize=12,
                transform=ax.transAxes
            )
            y_pos -= 0.15
            
        ax.set_title("Key Metrics", fontsize=14, fontweight='bold', pad=10)
        
    def create_ecommerce_dashboard(self):
        """Create dashboard for e-commerce data."""
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        self.create_header(fig, "E-Commerce Analytics Dashboard")
        
        # KPI Summary
        ax_kpi = fig.add_subplot(gs[0, 0])
        metrics = {
            "Total Revenue": f"${self.data['Total Price'].sum():,.0f}",
            "Total Orders": f"{len(self.data):,}",
            "Avg Order Value": f"${self.data['Total Price'].mean():.2f}",
            "Unique Customers": f"{self.data['Customer ID'].nunique():,}"
        }
        self.create_kpi_summary(ax_kpi, metrics)
        
        # Revenue distribution
        ax1 = fig.add_subplot(gs[0, 1:])
        sns.histplot(
            data=self.data, x="Total Price", bins=30,
            kde=True, ax=ax1, color='steelblue'
        )
        ax1.set_title("Revenue Distribution", fontweight='bold')
        ax1.set_xlabel("Order Value ($)")
        
        # Revenue by category
        ax2 = fig.add_subplot(gs[1, :2])
        category_revenue = self.data.groupby("Category")["Total Price"].sum().sort_values(ascending=False)
        sns.barplot(x=category_revenue.values, y=category_revenue.index, ax=ax2, palette="viridis")
        ax2.set_title("Revenue by Category", fontweight='bold')
        ax2.set_xlabel("Total Revenue ($)")
        
        # Top customers
        ax3 = fig.add_subplot(gs[1, 2])
        top_customers = self.data.groupby("Customer ID")["Total Price"].sum().nlargest(10)
        sns.barplot(y=top_customers.values, x=range(len(top_customers)), ax=ax3, palette="rocket")
        ax3.set_title("Top 10 Customers", fontweight='bold')
        ax3.set_ylabel("Total Spent ($)")
        ax3.set_xlabel("Customer Rank")
        
        # Quantity vs Price scatter
        ax4 = fig.add_subplot(gs[2, :2])
        sns.scatterplot(
            data=self.data, x="Quantity", y="Total Price",
            hue="Category", size="Quantity", sizes=(50, 300),
            alpha=0.6, ax=ax4
        )
        ax4.set_title("Quantity vs Total Price", fontweight='bold')
        ax4.legend(bbox_to_anchor=(1, 1), loc='upper left', fontsize=8)
        
        # Payment method distribution
        ax5 = fig.add_subplot(gs[2, 2])
        payment_counts = self.data["Payment Method"].value_counts()
        colors = sns.color_palette("Set2", len(payment_counts))
        ax5.pie(
            payment_counts.values,  # type: ignore[arg-type]
            labels=payment_counts.index.tolist(),  # type: ignore[arg-type]
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        ax5.set_title("Payment Methods", fontweight='bold')
        
        return fig
        
    def create_generic_dashboard(self):
        """Create generic dashboard for any dataset."""
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        self.create_header(fig, "Data Analysis Dashboard")
        
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) >= 2:
            # Distribution of first numeric column
            ax1 = fig.add_subplot(gs[0, 0])
            sns.histplot(data=self.data, x=numeric_cols[0], kde=True, ax=ax1)
            ax1.set_title(f"Distribution: {numeric_cols[0]}", fontweight='bold')
            
            # Distribution of second numeric column
            ax2 = fig.add_subplot(gs[0, 1])
            sns.histplot(data=self.data, x=numeric_cols[1], kde=True, ax=ax2)
            ax2.set_title(f"Distribution: {numeric_cols[1]}", fontweight='bold')
            
            # Correlation heatmap
            ax3 = fig.add_subplot(gs[1, 0])
            corr = self.data[numeric_cols].corr()  # type: ignore[call-arg]
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax3, center=0)
            ax3.set_title("Correlation Matrix", fontweight='bold')
            
            # Scatter plot
            ax4 = fig.add_subplot(gs[1, 1])
            sns.scatterplot(data=self.data, x=numeric_cols[0], y=numeric_cols[1], ax=ax4, alpha=0.6)
            ax4.set_title(f"{numeric_cols[1]} vs {numeric_cols[0]}", fontweight='bold')
        
        return fig
        
    def generate(self, dataset_type: str = "ecommerce") -> Figure:
        """Generate appropriate dashboard based on dataset type."""
        if dataset_type == "ecommerce":
            return self.create_ecommerce_dashboard()
        else:
            return self.create_generic_dashboard()


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Production dashboard generator")
    parser.add_argument(
        "--dataset",
        type=str,
        default="ecommerce_data",
        help="Dataset name (without .csv)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "exports" / "examples",
        help="Output directory"
    )
    parser.add_argument(
        "--format",
        type=str,
        nargs='+',
        default=["png"],
        choices=["png", "pdf", "svg"],
        help="Output format(s)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📊 PRODUCTION DASHBOARD GENERATOR")
    print("="*60 + "\n")
    
    # Apply theme
    apply_theme(style="whitegrid", context="notebook", palette="deep")
    
    # Load data
    data_path = Path(__file__).parent.parent / "datasets" / f"{args.dataset}.csv"
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {args.dataset}: {df.shape[0]} rows, {df.shape[1]} columns\n")
    
    # Generate dashboard
    print("Generating dashboard...\n")
    dashboard = DashboardGenerator(df, args.output)
    
    dataset_type = "ecommerce" if "ecommerce" in args.dataset else "generic"
    fig = dashboard.generate(dataset_type)
    
    # Save in multiple formats
    base_name = f"{args.dataset}_dashboard"
    save_publication_figure(fig, args.output / base_name, args.format)
    
    print(f"\n✅ Dashboard saved to: {args.output}")
    print(f"   Formats: {', '.join(args.format)}")
    print("\n" + "="*60 + "\n")
    
    plt.close()


if __name__ == "__main__":
    main()
