#!/usr/bin/env python3
"""
Batch Processing Multiple Datasets
===================================

Demonstrates how to process multiple datasets in batch and generate
consistent visualizations across all files.

Usage:
    python batch_processing.py
    python batch_processing.py --pattern "*.csv" --plots all
"""

import sys
from pathlib import Path
import argparse
from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from plot_utils import apply_theme, stylize_plot, save_fig, export_plot_data


class BatchProcessor:
    """Process multiple datasets in batch."""
    
    def __init__(self, data_dir: Path, output_dir: Path):
        """
        Initialize batch processor.
        
        Args:
            data_dir: Directory containing datasets
            output_dir: Directory for outputs
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def find_datasets(self, pattern: str = "*.csv") -> List[Path]:
        """Find all datasets matching pattern."""
        datasets = list(self.data_dir.glob(pattern))
        return sorted(datasets)
    
    def load_dataset(self, filepath: Path) -> pd.DataFrame:
        """Load a single dataset."""
        try:
            df = pd.read_csv(filepath)
            return df
        except Exception as e:
            print(f"  ⚠ Error loading {filepath.name}: {e}")
            return None
    
    def generate_summary_report(self, filepath: Path, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for a dataset."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        summary = {
            'filename': filepath.name,
            'rows': len(df),
            'columns': len(df.columns),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'missing_values': df.isnull().sum().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return summary
    
    def create_distribution_plots(self, filepath: Path, df: pd.DataFrame):
        """Create distribution plots for all numeric columns."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return
        
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if n_rows > 1 else axes
        
        for idx, col in enumerate(numeric_cols):
            ax = axes[idx] if len(numeric_cols) > 1 else axes[0]
            sns.histplot(data=df, x=col, kde=True, ax=ax, color='steelblue')
            ax.set_title(f"Distribution: {col}", fontweight='bold')
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")
        
        # Hide unused subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].axis('off')
        
        dataset_name = filepath.stem
        plt.suptitle(f"Distributions: {dataset_name}", fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        output_path = self.output_dir / dataset_name / "distributions.png"
        output_path.parent.mkdir(exist_ok=True)
        save_fig(output_path)
        plt.close()
    
    def create_correlation_matrix(self, filepath: Path, df: pd.DataFrame):
        """Create correlation heatmap."""
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return
        
        plt.figure(figsize=(10, 8))
        corr = df[numeric_cols].corr()
        
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={'shrink': 0.8}
        )
        
        dataset_name = filepath.stem
        plt.title(f"Correlation Matrix: {dataset_name}", fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        output_path = self.output_dir / dataset_name / "correlation.png"
        output_path.parent.mkdir(exist_ok=True)
        save_fig(output_path)
        plt.close()
    
    def create_category_overview(self, filepath: Path, df: pd.DataFrame):
        """Create overview of categorical columns."""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) == 0:
            return
        
        # Limit to columns with reasonable number of categories
        valid_cols = [col for col in categorical_cols if df[col].nunique() <= 20]
        
        if len(valid_cols) == 0:
            return
        
        n_cols = min(2, len(valid_cols))
        n_rows = (len(valid_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 5*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten() if n_rows > 1 else axes
        
        for idx, col in enumerate(valid_cols):
            ax = axes[idx] if len(valid_cols) > 1 else axes[0]
            value_counts = df[col].value_counts().head(10)
            
            sns.barplot(x=value_counts.values, y=value_counts.index, ax=ax, palette='viridis')
            ax.set_title(f"Top Values: {col}", fontweight='bold')
            ax.set_xlabel("Count")
        
        # Hide unused subplots
        for idx in range(len(valid_cols), len(axes)):
            axes[idx].axis('off')
        
        dataset_name = filepath.stem
        plt.suptitle(f"Categorical Overview: {dataset_name}", fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        output_path = self.output_dir / dataset_name / "categories.png"
        output_path.parent.mkdir(exist_ok=True)
        save_fig(output_path)
        plt.close()
    
    def process_single_dataset(self, filepath: Path, plot_types: List[str]) -> Dict:
        """Process a single dataset."""
        print(f"\n  Processing: {filepath.name}")
        
        df = self.load_dataset(filepath)
        if df is None:
            return None
        
        # Generate summary
        summary = self.generate_summary_report(filepath, df)
        print(f"    • {summary['rows']} rows, {summary['columns']} columns")
        
        # Create plots
        if 'distribution' in plot_types or 'all' in plot_types:
            self.create_distribution_plots(filepath, df)
            print("    ✓ Created distribution plots")
        
        if 'correlation' in plot_types or 'all' in plot_types:
            self.create_correlation_matrix(filepath, df)
            print("    ✓ Created correlation matrix")
        
        if 'category' in plot_types or 'all' in plot_types:
            self.create_category_overview(filepath, df)
            print("    ✓ Created category overview")
        
        # Export summary data
        summary_path = self.output_dir / filepath.stem / "summary.json"
        summary_path.parent.mkdir(exist_ok=True)
        export_plot_data(None, summary, str(summary_path), 'json')
        
        return summary
    
    def process_all(self, pattern: str = "*.csv", plot_types: List[str] = ['all'], 
                    parallel: bool = False) -> List[Dict]:
        """Process all datasets."""
        datasets = self.find_datasets(pattern)
        
        if len(datasets) == 0:
            print(f"⚠ No datasets found matching pattern: {pattern}")
            return []
        
        print(f"\nFound {len(datasets)} datasets to process")
        
        summaries = []
        
        if parallel and len(datasets) > 1:
            # Parallel processing
            print("\n🚀 Processing in parallel...")
            with ProcessPoolExecutor() as executor:
                futures = {
                    executor.submit(self.process_single_dataset, fp, plot_types): fp 
                    for fp in datasets
                }
                
                for future in as_completed(futures):
                    summary = future.result()
                    if summary:
                        summaries.append(summary)
        else:
            # Sequential processing
            for filepath in datasets:
                summary = self.process_single_dataset(filepath, plot_types)
                if summary:
                    summaries.append(summary)
        
        return summaries
    
    def create_master_report(self, summaries: List[Dict]):
        """Create a master comparison report."""
        if not summaries:
            return
        
        df_summary = pd.DataFrame(summaries)
        
        # Create comparison visualization
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Dataset sizes
        ax = axes[0, 0]
        sns.barplot(data=df_summary, x='filename', y='rows', ax=ax, palette='Set2')
        ax.set_title("Dataset Sizes (Rows)", fontweight='bold')
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=45)
        
        # Column counts
        ax = axes[0, 1]
        sns.barplot(data=df_summary, x='filename', y='columns', ax=ax, palette='Set3')
        ax.set_title("Number of Columns", fontweight='bold')
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=45)
        
        # Missing values
        ax = axes[1, 0]
        sns.barplot(data=df_summary, x='filename', y='missing_values', ax=ax, palette='Reds_r')
        ax.set_title("Missing Values", fontweight='bold')
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=45)
        
        # Memory usage
        ax = axes[1, 1]
        sns.barplot(data=df_summary, x='filename', y='memory_usage_mb', ax=ax, palette='Blues')
        ax.set_title("Memory Usage (MB)", fontweight='bold')
        ax.set_xlabel("")
        ax.tick_params(axis='x', rotation=45)
        
        plt.suptitle("Dataset Comparison Report", fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        save_fig(self.output_dir / "master_report.png")
        plt.close()
        
        # Export summary table
        export_path = self.output_dir / "batch_summary.csv"
        df_summary.to_csv(export_path, index=False)
        print(f"\n  ✓ Master report saved: {export_path}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Batch dataset processing")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "datasets",
        help="Directory containing datasets"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "exports" / "batch_processing",
        help="Output directory"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.csv",
        help="File pattern to match"
    )
    parser.add_argument(
        "--plots",
        type=str,
        nargs='+',
        default=['all'],
        choices=['all', 'distribution', 'correlation', 'category'],
        help="Types of plots to generate"
    )
    parser.add_argument(
        "--parallel",
        action='store_true',
        help="Process datasets in parallel"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🔄 BATCH DATASET PROCESSING")
    print("="*60)
    
    # Setup theme
    apply_theme(style="whitegrid", context="notebook", palette="deep")
    
    # Process datasets
    processor = BatchProcessor(args.data_dir, args.output)
    summaries = processor.process_all(args.pattern, args.plots, args.parallel)
    
    # Create master report
    if summaries:
        print("\nCreating master comparison report...")
        processor.create_master_report(summaries)
    
    print("\n" + "="*60)
    print(f"✅ Processed {len(summaries)} datasets")
    print(f"📁 Output directory: {args.output}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
