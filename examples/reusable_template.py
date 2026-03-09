#!/usr/bin/env python3
"""
Reusable Visualization Template
================================

A production-ready template for creating Seaborn visualizations.
Copy and modify this file for your own projects.

Usage:
    python reusable_template.py --help
    python reusable_template.py --data my_data.csv --x column1 --y column2
"""

import sys
from pathlib import Path
import argparse
import logging
from typing import Optional, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import (
    apply_theme,
    stylize_plot,
    save_fig,
    save_publication_figure,
    export_plot_data
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VisualizationPipeline:
    """
    Reusable visualization pipeline.
    
    This class provides a structured approach to creating visualizations
    with proper error handling, logging, and output management.
    """
    
    def __init__(self, 
                 data_path: Path,
                 output_dir: Path,
                 theme_style: str = 'whitegrid',
                 color_palette: str = 'deep'):
        """
        Initialize visualization pipeline.
        
        Args:
            data_path: Path to input data file
            output_dir: Directory for saving outputs
            theme_style: Seaborn style theme
            color_palette: Color palette name
        """
        self.data_path = data_path
        self.output_dir = output_dir
        self.theme_style = theme_style
        self.color_palette = color_palette
        self.data = None
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Apply theme
        apply_theme(style=theme_style, palette=color_palette)
        
        logger.info(f"Initialized pipeline with style={theme_style}, palette={color_palette}")
    
    def load_data(self, **kwargs) -> pd.DataFrame:
        """
        Load data from file.
        
        Args:
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            Loaded DataFrame
        """
        try:
            logger.info(f"Loading data from {self.data_path}")
            
            if self.data_path.suffix == '.csv':
                self.data = pd.read_csv(self.data_path, **kwargs)
            elif self.data_path.suffix in ['.xlsx', '.xls']:
                self.data = pd.read_excel(self.data_path, **kwargs)
            elif self.data_path.suffix == '.json':
                self.data = pd.read_json(self.data_path, **kwargs)
            else:
                raise ValueError(f"Unsupported file format: {self.data_path.suffix}")
            
            logger.info(f"Successfully loaded {len(self.data)} rows, {len(self.data.columns)} columns")
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def validate_columns(self, required_cols: List[str]) -> bool:
        """
        Validate that required columns exist in data.
        
        Args:
            required_cols: List of required column names
            
        Returns:
            True if all columns exist
        """
        if self.data is None:
            logger.error("Data not loaded. Call load_data() first.")
            return False
        
        missing = [col for col in required_cols if col not in self.data.columns]
        
        if missing:
            logger.error(f"Missing required columns: {missing}")
            logger.info(f"Available columns: {list(self.data.columns)}")
            return False
        
        return True
    
    def create_scatter_plot(self, 
                           x: str, 
                           y: str, 
                           hue: Optional[str] = None,
                           title: Optional[str] = None,
                           filename: Optional[str] = None) -> Figure:
        """
        Create a scatter plot.
        
        Args:
            x: Column name for x-axis
            y: Column name for y-axis
            hue: Column name for color grouping
            title: Plot title
            filename: Output filename (without extension)
            
        Returns:
            Figure object
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        required_cols = [x, y]
        if hue:
            required_cols.append(hue)
        
        if not self.validate_columns(required_cols):
            raise ValueError("Cannot create plot: missing required columns")
        
        logger.info(f"Creating scatter plot: {x} vs {y}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.scatterplot(
            data=self.data,
            x=x,
            y=y,
            hue=hue,
            s=100,
            alpha=0.7,
            ax=ax
        )
        
        plot_title = title or f"{y} vs {x}"
        stylize_plot(title=plot_title, xlabel=x, ylabel=y)
        
        if hue:
            plt.legend(title=hue, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        if filename:
            save_fig(self.output_dir / f"{filename}.png")
            logger.info(f"Saved plot to {filename}.png")
        
        return fig
    
    def create_distribution_plot(self,
                                column: str,
                                title: Optional[str] = None,
                                filename: Optional[str] = None) -> Figure:
        """
        Create a distribution plot with histogram and KDE.
        
        Args:
            column: Column name to plot
            title: Plot title
            filename: Output filename
            
        Returns:
            Figure object
        """
        if not self.validate_columns([column]):
            raise ValueError("Cannot create plot: column not found")
        
        logger.info(f"Creating distribution plot for {column}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.histplot(
            data=self.data,
            x=column,
            kde=True,
            bins=30,
            ax=ax
        )
        
        plot_title = title or f"Distribution of {column}"
        stylize_plot(title=plot_title, xlabel=column, ylabel="Frequency")
        
        if filename:
            save_fig(self.output_dir / f"{filename}.png")
            logger.info(f"Saved plot to {filename}.png")
        
        return fig
    
    def create_categorical_plot(self,
                               x: str,
                               y: str,
                               kind: str = 'bar',
                               title: Optional[str] = None,
                               filename: Optional[str] = None) -> Figure:
        """
        Create a categorical plot.
        
        Args:
            x: Categorical column name
            y: Numeric column name
            kind: Plot type ('bar', 'box', 'violin', 'point')
            title: Plot title
            filename: Output filename
            
        Returns:
            Figure object
        """
        if not self.validate_columns([x, y]):
            raise ValueError("Cannot create plot: missing required columns")
        
        logger.info(f"Creating {kind} plot: {y} by {x}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if kind == 'bar':
            sns.barplot(data=self.data, x=x, y=y, ci=95, ax=ax)
        elif kind == 'box':
            sns.boxplot(data=self.data, x=x, y=y, ax=ax)
        elif kind == 'violin':
            sns.violinplot(data=self.data, x=x, y=y, ax=ax)
        elif kind == 'point':
            sns.pointplot(data=self.data, x=x, y=y, ci=95, ax=ax)
        else:
            raise ValueError(f"Unknown plot kind: {kind}")
        
        plot_title = title or f"{y} by {x}"
        stylize_plot(title=plot_title, xlabel=x, ylabel=y)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if filename:
            save_fig(self.output_dir / f"{filename}.png")
            logger.info(f"Saved plot to {filename}.png")
        
        return fig
    
    def create_correlation_heatmap(self,
                                  title: Optional[str] = None,
                                  filename: Optional[str] = None) -> Optional[Figure]:
        """
        Create correlation heatmap for numeric columns.
        
        Args:
            title: Plot title
            filename: Output filename
            
        Returns:
            Figure object
        """
        if self.data is None:
            logger.error("Data not loaded. Call load_data() first.")
            return None
            
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            logger.warning("Not enough numeric columns for correlation matrix")
            return None
        
        logger.info(f"Creating correlation heatmap with {len(numeric_cols)} columns")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        corr = self.data[numeric_cols].corr()
        
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={'shrink': 0.8},
            ax=ax
        )
        
        plot_title = title or "Correlation Matrix"
        plt.title(plot_title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if filename:
            save_fig(self.output_dir / f"{filename}.png")
            logger.info(f"Saved plot to {filename}.png")
        
        return fig
    
    def export_summary(self, filename: str = "summary"):
        """
        Export data summary statistics.
        
        Args:
            filename: Output filename (without extension)
        """
        if self.data is None:
            logger.warning("No data loaded to export")
            return
            
        logger.info("Exporting summary statistics")
        
        summary = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.astype(str).to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'numeric_summary': self.data.describe().to_dict()
        }
        
        export_plot_data(None, summary, str(self.output_dir / f"{filename}.json"), 'json')
        logger.info(f"Summary exported to {filename}.json")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Reusable visualization template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --data sales.csv --x Quantity --y Revenue
  %(prog)s --data data.csv --dist Price --cat Category Product
  %(prog)s --data data.csv --heatmap
        """
    )
    
    # Input/Output
    parser.add_argument('--data', type=Path, required=True, help='Input data file')
    parser.add_argument('--output', type=Path, default=Path('./output'),
                       help='Output directory')
    
    # Plot types
    parser.add_argument('--scatter', action='store_true', help='Create scatter plot')
    parser.add_argument('--dist', type=str, help='Create distribution plot for column')
    parser.add_argument('--cat', nargs=2, metavar=('X', 'Y'),
                       help='Create categorical plot (x y)')
    parser.add_argument('--heatmap', action='store_true', help='Create correlation heatmap')
    
    # Plot parameters
    parser.add_argument('--x', type=str, help='X-axis column')
    parser.add_argument('--y', type=str, help='Y-axis column')
    parser.add_argument('--hue', type=str, help='Hue grouping column')
    parser.add_argument('--kind', type=str, default='bar',
                       choices=['bar', 'box', 'violin', 'point'],
                       help='Categorical plot type')
    
    # Styling
    parser.add_argument('--style', type=str, default='whitegrid',
                       choices=['darkgrid', 'whitegrid', 'dark', 'white', 'ticks'],
                       help='Plot style')
    parser.add_argument('--palette', type=str, default='deep',
                       help='Color palette')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    print("\n" + "="*60)
    print("🎨 VISUALIZATION PIPELINE")
    print("="*60 + "\n")
    
    pipeline = VisualizationPipeline(
        data_path=args.data,
        output_dir=args.output,
        theme_style=args.style,
        color_palette=args.palette
    )
    
    # Load data
    pipeline.load_data()
    
    # Create plots based on arguments
    plots_created = 0
    
    if args.scatter and args.x and args.y:
        pipeline.create_scatter_plot(args.x, args.y, args.hue, filename='scatter')
        plots_created += 1
    
    if args.dist:
        pipeline.create_distribution_plot(args.dist, filename='distribution')
        plots_created += 1
    
    if args.cat:
        pipeline.create_categorical_plot(args.cat[0], args.cat[1], args.kind, filename='categorical')
        plots_created += 1
    
    if args.heatmap:
        pipeline.create_correlation_heatmap(filename='heatmap')
        plots_created += 1
    
    # Export summary
    pipeline.export_summary()
    
    print("\n" + "="*60)
    print(f"✅ Created {plots_created} visualization(s)")
    print(f"📁 Output directory: {args.output}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
