"""Smoke tests for the Streamlit explorer using ``streamlit.testing.v1.AppTest``."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "streamlit_app.py"


def _run(**kwargs):
    return AppTest.from_file(str(APP), default_timeout=60).run(**kwargs)


def _by_key(widgets, key):
    return next(w for w in widgets if w.key == key)


@pytest.fixture(scope="module")
def app():
    return _run()


class TestDefaultRender:
    def test_no_exception(self, app):
        assert not app.exception

    def test_five_tabs(self, app):
        assert len(app.tabs) == 5

    def test_gallery_has_all_sections(self, app):
        options = _by_key(app.selectbox, "gallery_section").options
        assert len(options) == 11
        assert options[-1] == "🔬 11 - Research Workflow"

    def test_datasets_tab_renders_card_and_plot(self, app):
        assert _by_key(app.selectbox, "ds_name").value == "sales_data"
        assert _by_key(app.radio, "ds_kind").value == "scatter"
        assert any("Generative model" in m.value for m in app.markdown)
        assert len(app.dataframe) >= 3

    def test_compare_tab_runs_default_test(self, app):
        assert _by_key(app.selectbox, "cmp_test").value == "welch"
        assert _by_key(app.selectbox, "cmp_corr").value == "holm"
        assert any("pairwise comparisons" in m.value for m in app.markdown)

    def test_palette_tab_reports_metrics(self, app):
        assert _by_key(app.selectbox, "pal_name").value == "colorblind"
        assert app.success or app.error  # pass/fail banner is always shown

    def test_environment_tab_lists_manifest(self, app):
        assert any("match the manifest" in s.value for s in app.success) or any(
            "differ from the manifest" in e.value for e in app.error
        )


class TestInteractions:
    def test_gallery_research_section(self):
        at = _run()
        _by_key(at.selectbox, "gallery_section").set_value("🔬 11 - Research Workflow")
        at.run()
        assert not at.exception

    @pytest.mark.parametrize("kind", ["box", "violin", "hist", "line"])
    def test_dataset_plot_kinds(self, kind):
        at = _run()
        _by_key(at.selectbox, "ds_name").set_value("clinical_trial")
        at.run()
        _by_key(at.radio, "ds_kind").set_value(kind)
        at.run()
        assert not at.exception

    def test_dataset_plot_with_hue(self):
        at = _run()
        _by_key(at.selectbox, "ds_name").set_value("clinical_trial")
        at.run()
        _by_key(at.selectbox, "ds_hue").set_value("Arm")
        at.run()
        assert not at.exception

    @pytest.mark.parametrize("test", ["student", "mannwhitney", "permutation"])
    def test_compare_tests(self, test):
        at = _run()
        _by_key(at.selectbox, "cmp_name").set_value("clinical_trial")
        at.run()
        assert _by_key(at.selectbox, "cmp_x").value == "Arm"
        assert _by_key(at.selectbox, "cmp_y").value == "Outcome"
        _by_key(at.selectbox, "cmp_test").set_value(test)
        _by_key(at.selectbox, "cmp_corr").set_value("fdr_bh")
        _by_key(at.slider, "cmp_nperm").set_value(200)
        at.run()
        assert not at.exception
        assert any("3 pairwise comparisons" in m.value for m in at.markdown)

    def test_compare_caps_levels_with_warning(self):
        at = _run()
        _by_key(at.selectbox, "cmp_name").set_value("gene_expression")
        at.run()
        _by_key(at.selectbox, "cmp_x").set_value("Gene")
        at.run()
        assert not at.exception
        # Every gene is a singleton level: all are dropped and the tab explains why.
        assert any("fewer than 2 observations" in w.value for w in at.warning)
        assert any("at least two groups" in i.value for i in at.info)

    def test_compare_caps_number_of_levels(self):
        at = _run()
        _by_key(at.selectbox, "cmp_name").set_value("clinical_trial")
        at.run()
        _by_key(at.selectbox, "cmp_x").set_value("Site")
        at.run()
        assert not at.exception
        assert any("3 pairwise comparisons" in m.value for m in at.markdown)

    def test_custom_hex_palette(self):
        at = _run()
        _by_key(at.radio, "pal_mode").set_value("Custom hex")
        at.run()
        _by_key(at.text_input, "pal_hex").set_value("#000000, #FFFFFF, #FF0000")
        at.run()
        assert not at.exception
        assert any("Palette `custom`" in c.value for c in at.caption)

    def test_invalid_hex_is_reported(self):
        at = _run()
        _by_key(at.radio, "pal_mode").set_value("Custom hex")
        at.run()
        _by_key(at.text_input, "pal_hex").set_value("#000000, not-a-colour")
        at.run()
        assert not at.exception
        assert any("Could not parse colours" in e.value for e in at.error)
