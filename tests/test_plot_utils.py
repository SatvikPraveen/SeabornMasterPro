"""Backward-compatibility tests for the ``utils.plot_utils`` facade."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utils
from utils.plot_utils import (
    apply_theme,
    create_color_palette,
    create_plot_grid,
    export_plot_data,
    save_fig,
)


def test_facade_exports_everything():
    assert set(utils.__all__) >= {
        "apply_theme",
        "save_fig",
        "stylize_plot",
        "compare_groups",
        "annotate_pairwise",
    }
    assert utils.__version__ == "2.0.0"


def test_legacy_workflow(tmp_path, sample_data):
    apply_theme()
    palette = create_color_palette(n_colors=3)
    plt.figure(figsize=(6, 4))
    sns.scatterplot(data=sample_data, x="x", y="y", hue="category", palette=palette)
    out = tmp_path / "integration_plot.png"
    save_fig(str(out))
    export_plot_data(None, sample_data, str(tmp_path / "data.csv"))
    assert out.exists() and (tmp_path / "data.csv").exists()
    assert len(pd.read_csv(tmp_path / "data.csv")) == len(sample_data)


def test_legacy_grid_signature():
    _fig, axes = create_plot_grid(2, 2)
    assert len(axes) == 4
