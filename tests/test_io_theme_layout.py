import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns
from PIL import Image

from seabornmasterpro import annotate, io, layout, stats, theme


class TestSaveFig:
    def test_creates_dirs_and_png_metadata(self, tmp_path):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        out = tmp_path / "nested" / "dir" / "plot.png"
        path = io.save_fig(out, fig=fig, title="My plot", verbose=False)
        assert path.exists() and path.stat().st_size > 0
        with Image.open(path) as im:
            info = im.info
        assert info["Title"] == "My plot"
        prov = json.loads(info["Provenance"])
        assert "python" in prov and "packages" in prov and "seaborn" in prov["packages"]

    def test_sidecar(self, tmp_path):
        fig, _ax = plt.subplots()
        io.save_fig(tmp_path / "p.png", fig=fig, sidecar=True, verbose=False)
        side = tmp_path / "p.png.json"
        assert side.exists()
        assert "timestamp_utc" in json.loads(side.read_text())

    def test_no_provenance(self, tmp_path):
        fig, _ax = plt.subplots()
        io.save_fig(tmp_path / "p.png", fig=fig, provenance=False, verbose=False)
        with Image.open(tmp_path / "p.png") as im:
            assert "Provenance" not in im.info

    def test_uses_current_figure(self, tmp_path):
        plt.figure()
        plt.plot([0, 1])
        io.save_fig(tmp_path / "cur.png", verbose=False)
        assert (tmp_path / "cur.png").exists()

    @pytest.mark.parametrize("fmt", ["pdf", "svg"])
    def test_vector_formats(self, tmp_path, fmt):
        fig, ax = plt.subplots()
        ax.plot([1, 2])
        p = io.save_fig(tmp_path / f"v.{fmt}", fig=fig, verbose=False)
        assert p.exists() and p.stat().st_size > 0

    def test_publication_multi_format(self, tmp_path):
        fig, ax = plt.subplots()
        ax.plot([1, 2])
        paths = io.save_publication_figure(
            fig, tmp_path / "pub", formats=("png", "pdf", "svg"), dpi=72, verbose=False
        )
        assert [p.suffix for p in paths] == [".png", ".pdf", ".svg"]
        assert all(p.exists() for p in paths)


class TestExportData:
    def test_csv_roundtrip(self, tmp_path):
        df = pd.DataFrame({"A": [1, 2], "B": [3.5, 4.5]})
        p = io.export_plot_data(None, df, tmp_path / "d.csv", verbose=False)
        pd.testing.assert_frame_equal(pd.read_csv(p), df)

    def test_json_and_dict(self, tmp_path):
        p = io.export_plot_data(None, {"A": [1, 2]}, tmp_path / "d.json", verbose=False)
        assert json.loads(p.read_text()) == [{"A": 1}, {"A": 2}]

    def test_format_override_and_none(self, tmp_path):
        assert io.export_plot_data(None, None, tmp_path / "x.csv") is None
        p = io.export_plot_data(
            None, {"A": [1]}, tmp_path / "data.txt", format="csv", verbose=False
        )
        assert p.read_text().startswith("A")

    def test_bad_format(self, tmp_path):
        with pytest.raises(ValueError):
            io.export_plot_data(None, {"A": [1]}, tmp_path / "d.xyz", verbose=False)


class TestTheme:
    def test_apply_theme(self):
        theme.apply_theme(style="dark", context="talk", palette="Set2", font_scale=1.1)
        assert matplotlib.rcParams["axes.facecolor"] != "white"

    @pytest.mark.parametrize("journal", list(theme.JOURNALS))
    def test_publication_rc_has_figsize(self, journal):
        rc = theme.publication_rc(journal, columns=2)
        w, h = rc["figure.figsize"]
        assert w == pytest.approx(theme.JOURNALS[journal].double_column)
        assert h <= theme.JOURNALS[journal].max_height
        assert rc["pdf.fonttype"] == 42

    def test_journal_context_restores(self):
        before = matplotlib.rcParams["font.size"]
        with theme.journal_context("nature") as spec:
            assert spec.name == "Nature"
            assert matplotlib.rcParams["font.size"] == spec.font_size
        assert matplotlib.rcParams["font.size"] == before

    def test_figsize_for(self):
        w, h = theme.figsize_for("ieee", columns=1, aspect=1.0)
        assert w == 3.5 and h == 3.5

    def test_unknown_journal(self):
        with pytest.raises(KeyError):
            theme.publication_rc("cell")


class TestLayout:
    def test_plot_grid_flat(self):
        _fig, axes = layout.create_plot_grid(2, 3)
        assert axes.shape == (6,)
        _fig1, axes1 = layout.create_plot_grid(1, 1)
        assert axes1.shape == (1,)

    def test_plot_grid_invalid(self):
        with pytest.raises(ValueError):
            layout.create_plot_grid(0, 2)

    def test_plot_comparison(self, sample_data):
        _fig, axes = layout.plot_comparison(
            sns.histplot, sample_data, [{"x": "x"}, {"x": "y", "kde": True}], ["x", "y"]
        )
        assert len(axes) == 2 and axes[1].get_title() == "y"

    def test_plot_comparison_mismatch(self, sample_data):
        with pytest.raises(ValueError):
            layout.plot_comparison(sns.histplot, sample_data, [{"x": "x"}], ["a", "b"])

    def test_label_panels(self):
        _fig, axes = layout.create_plot_grid(1, 3)
        layout.label_panels(axes, fmt="({})", uppercase=False)
        assert [t.get_text() for ax in axes for t in ax.texts] == ["(a)", "(b)", "(c)"]

    @pytest.mark.parametrize("loc", ["year", "month", "week", "day", "auto"])
    def test_format_date_axis(self, loc):
        dates = pd.date_range("2024-01-01", periods=90)
        _fig, ax = plt.subplots()
        ax.plot(dates, np.arange(90))
        out = layout.format_date_axis(ax, major_locator=loc)
        assert out is ax

    def test_format_date_axis_bad(self):
        _fig, ax = plt.subplots()
        with pytest.raises(ValueError):
            layout.format_date_axis(ax, major_locator="fortnight")


class TestAnnotate:
    def test_stylize_and_reference(self):
        _fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        annotate.stylize_plot("T", "X", "Y", rotate_xticks=45, ax=ax)
        assert ax.get_title() == "T" and ax.get_xlabel() == "X"
        line = annotate.add_reference_line(2, "h", ax=ax, label="ref")
        assert line.get_label() == "ref"
        annotate.add_reference_line(1, "v", ax=ax)
        with pytest.raises(ValueError):
            annotate.add_reference_line(1, "diag", ax=ax)

    def test_annotate_points(self):
        _fig, ax = plt.subplots()
        annotate.annotate_points([0, 1], [0, 1], labels=["a", "b"], ax=ax)
        assert [t.get_text() for t in ax.texts] == ["a", "b"]

    def test_single_bracket(self):
        _fig, ax = plt.subplots()
        annotate.add_statistical_annotations(ax, 0, 1, 1.0, 0.003)
        assert ax.texts[0].get_text() == "**"

    def test_annotate_pairwise_stacks_and_expands_ylim(self, three_groups):
        _fig, ax = plt.subplots()
        sns.boxplot(data=three_groups, x="g", y="y", ax=ax)
        top_before = ax.get_ylim()[1]
        res = stats.compare_groups(three_groups, "g", "y")
        annotate.annotate_pairwise(ax, res, show_effect=True)
        assert len(ax.texts) == 3
        assert ax.get_ylim()[1] > top_before
        assert all("g=" in t.get_text() for t in ax.texts)

    def test_annotate_pairwise_only_significant(self, rng):
        df = pd.DataFrame({"g": np.repeat(["A", "B"], 30), "y": rng.normal(size=60)})
        _fig, ax = plt.subplots()
        sns.barplot(data=df, x="g", y="y", ax=ax)
        res = stats.compare_groups(df, "g", "y")
        res["p_adjusted"] = 0.9
        res["stars"] = "ns"
        annotate.annotate_pairwise(ax, res, only_significant=True)
        assert len(ax.texts) == 0

    def test_annotate_effect_sizes(self, three_groups):
        _fig, ax = plt.subplots()
        sns.barplot(data=three_groups, x="g", y="y", ax=ax)
        summary = stats.group_summary(three_groups, "g", "y", n_boot=100)
        annotate.annotate_effect_sizes(ax, summary, "g")
        assert len(ax.texts) == 3


class TestPolish:
    def test_font_family_override(self):
        rc = theme.publication_rc("ieee", font_family=("DejaVu Serif",))
        assert rc["font.serif"] == ["DejaVu Serif"] and rc["font.family"] == "serif"
        rc = theme.publication_rc("nature", font_family=("DejaVu Sans",))
        assert rc["font.family"] == "sans-serif"
        with theme.journal_context("ieee", font_family=("DejaVu Serif",)):
            import matplotlib as mpl

            assert mpl.rcParams["font.serif"] == ["DejaVu Serif"]

    def test_annotate_effect_sizes_reserves_space(self, three_groups):
        from seabornmasterpro import stats

        summary = stats.group_summary(three_groups, "g", "y", n_boot=100)
        _fig, ax = plt.subplots()
        sns.stripplot(data=three_groups, x="g", y="y", ax=ax)
        y0, _ = ax.get_ylim()
        annotate.annotate_effect_sizes(ax, summary, "g")
        assert ax.get_ylim()[0] < y0
        _fig2, ax2 = plt.subplots()
        sns.stripplot(data=three_groups, x="g", y="y", ax=ax2)
        lim = ax2.get_ylim()
        annotate.annotate_effect_sizes(ax2, summary, "g", pad=0)
        assert ax2.get_ylim() == lim

    def test_write_json_nested_and_numpy(self, tmp_path):
        import json

        import numpy as np

        payload = {"a": {"b": np.float64(1.5), "c": np.arange(3)}, "d": [1, 2]}
        path = io.write_json(payload, tmp_path / "meta.json", provenance=True, verbose=False)
        loaded = json.loads(path.read_text())
        assert loaded["data"]["a"]["c"] == [0, 1, 2] and loaded["data"]["a"]["b"] == 1.5
        assert "packages" in loaded["provenance"]
