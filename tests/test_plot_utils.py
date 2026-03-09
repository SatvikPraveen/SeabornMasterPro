"""
Unit tests for plot_utils.py functions.

Run with: pytest tests/test_plot_utils.py
"""

import pytest
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.plot_utils import (
    apply_theme,
    save_fig,
    create_color_palette,
    export_plot_data,
    create_plot_grid
)


class TestApplyTheme:
    """Test theme application."""
   
    def test_apply_theme_default(self):
        """Test applying default theme."""
        apply_theme()
        # Should not raise any errors
        assert True

    def test_apply_theme_custom(self):
        """Test applying custom theme."""
        apply_theme(style="dark", context="talk", palette="Set2")
        # Should not raise any errors
        assert True


class TestSaveFig:
    """Test figure saving."""
   
    def test_save_fig_creates_directory(self, tmp_path):
        """Test that save_fig creates directory if it doesn't exist."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
       
        output_path = tmp_path / "test_output" / "plot.png"
        save_fig(str(output_path))
       
        assert output_path.exists()
        plt.close(fig)
   
    def test_save_fig_creates_file(self, tmp_path):
        """Test that save_fig creates the file."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 2, 3])
       
        output_path = tmp_path / "plot.png"
        save_fig(str(output_path))
       
        assert output_path.exists()
        assert output_path.stat().st_size > 0  # File not empty
        plt.close(fig)


class TestCreateColorPalette:
    """Test color palette creation."""
   
    def test_default_qualitative_palette(self):
        """Test creating default qualitative palette."""
        palette = create_color_palette(n_colors=5)
        assert len(palette) == 5
   
    def test_custom_colors(self):
        """Test creating palette from custom colors."""
        custom = ['red', 'blue', 'green']
        palette = create_color_palette(colors=custom)
        assert len(palette) == 3
   
    def test_sequential_palette(self):
        """Test creating sequential palette."""
        palette = create_color_palette(palette_type="sequential", n_colors=8)
        assert len(palette) == 8
   
    def test_diverging_palette(self):
        """Test creating diverging palette."""
        palette = create_color_palette(palette_type="diverging", n_colors=11)
        assert len(palette) == 11


class TestExportPlotData:
    """Test data export functionality."""
   
    def test_export_csv(self, tmp_path):
        """Test exporting data to CSV."""
        data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        output_path = tmp_path / "data.csv"
       
        export_plot_data(None, data, str(output_path), format='csv')
       
        assert output_path.exists()
        loaded = pd.read_csv(output_path)
        pd.testing.assert_frame_equal(data, loaded)
   
    def test_export_json(self, tmp_path):
        """Test exporting data to JSON."""
        data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        output_path = tmp_path / "data.json"
       
        export_plot_data(None, data, str(output_path), format='json')
       
        assert output_path.exists()
   
    def test_export_dict(self, tmp_path):
        """Test exporting dictionary data."""
        data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        output_path = tmp_path / "data.csv"
       
        export_plot_data(None, data, str(output_path))
       
        assert output_path.exists()


class TestCreatePlotGrid:
    """Test plot grid creation."""
   
    def test_single_plot(self):
        """Test creating 1x1 grid."""
        fig, axes = create_plot_grid(1, 1)
        assert fig is not None
        assert len(axes) == 1
        plt.close(fig)
   
    def test_multiple_plots(self):
        """Test creating 2x2 grid."""
        fig, axes = create_plot_grid(2, 2)
        assert fig is not None
        assert len(axes) == 4
        plt.close(fig)
   
    def test_custom_figsize(self):
        """Test creating grid with custom figsize."""
        fig, axes = create_plot_grid(2, 3, figsize=(12, 8))
        assert fig is not None
        assert len(axes) == 6
        plt.close(fig)


# Fixtures
@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })


class TestIntegration:
    """Integration tests using real plots."""
   
    def test_complete_workflow(self, tmp_path, sample_data):
        """Test complete plotting workflow."""
        # Apply theme
        apply_theme()
       
        # Create palette
        palette = create_color_palette(n_colors=3)
       
        # Create plot
        plt.figure(figsize=(8, 6))
       
        sns.scatterplot(data=sample_data, x='x', y='y', 
                       hue='category', palette=palette)
       
        # Save figure
        output_path = tmp_path / "integration_plot.png"
        save_fig(str(output_path))
       
        # Export data
        data_path = tmp_path / "data.csv"
        export_plot_data(None, sample_data, str(data_path))
       
        # Verify
        assert output_path.exists()
        assert data_path.exists()
       
        plt.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
