import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from seabornmasterpro import color as C

unit = st.floats(0.0, 1.0)
rgb = st.tuples(unit, unit, unit)


class TestConversions:
    @given(c=rgb)
    @settings(max_examples=100, deadline=None)
    def test_srgb_roundtrip(self, c):
        arr = np.array(c)
        assert np.allclose(C.linear_to_srgb(C.srgb_to_linear(arr)), arr, atol=1e-9)

    def test_lab_reference_values(self):
        lab = C.rgb_to_lab(np.array([[1, 1, 1], [0, 0, 0], [1, 0, 0]]))
        assert lab[0] == pytest.approx([100, 0, 0], abs=0.05)
        assert lab[1] == pytest.approx([0, 0, 0], abs=1e-6)
        assert lab[2] == pytest.approx([53.24, 80.09, 67.20], abs=0.05)

    def test_luminance_and_contrast(self):
        assert C.relative_luminance("white") == pytest.approx(1.0)
        assert C.relative_luminance("black") == pytest.approx(0.0)
        assert C.contrast_ratio("white", "black") == pytest.approx(21.0)
        assert C.contrast_ratio("black", "white") == pytest.approx(21.0)
        assert C.contrast_ratio("#777777", "white") == pytest.approx(4.48, abs=0.02)

    def test_delta_e(self):
        assert C.delta_e("red", "red") == 0
        assert C.delta_e("red", "green") > 100
        assert C.delta_e("#000000", "#010101") < 1


class TestCVD:
    @pytest.mark.parametrize("kind", ["protanopia", "deuteranopia", "tritanopia", "achromatopsia"])
    def test_output_shape_and_range(self, kind):
        out = C.simulate_cvd("tab10", kind)
        assert out.shape == (10, 3)
        assert out.min() >= 0 and out.max() <= 1

    def test_white_and_black_preserved(self):
        for kind in ("protanopia", "deuteranopia", "tritanopia"):
            out = C.simulate_cvd(["white", "black"], kind)
            assert out[0] == pytest.approx([1, 1, 1], abs=0.02)
            assert out[1] == pytest.approx([0, 0, 0], abs=0.02)

    def test_red_green_collapse_under_deuteranopia(self):
        normal, _ = C.min_pairwise_distance(["red", "green"])
        sim, _ = C.min_pairwise_distance(C.simulate_cvd(["red", "green"], "deuteranopia"))
        assert sim < normal * 0.6

    def test_achromatopsia_is_gray(self):
        out = C.simulate_cvd(["red", "blue", "#33aa55"], "achromatopsia")
        assert np.allclose(out[:, 0], out[:, 1]) and np.allclose(out[:, 1], out[:, 2])

    def test_bad_kind(self):
        with pytest.raises(ValueError):
            C.simulate_cvd(["red"], "monochromacy")  # type: ignore[arg-type]

    def test_grid_keys(self):
        grid = C.cvd_palette_grid("deep")
        assert set(grid) == {"normal", "protanopia", "deuteranopia", "tritanopia", "achromatopsia"}


class TestValidate:
    def test_colorblind_palette_distinguishable(self):
        r = C.validate_palette("colorblind")
        assert r.distinguishable
        assert r.n_colors == 10
        assert all(v >= 10 for v in r.min_delta_e_cvd.values())

    def test_set2_not_cvd_safe(self):
        r = C.validate_palette("Set2")
        assert not r.distinguishable
        assert any("protanopia" in w for w in r.warnings)

    def test_contrast_flag(self):
        r = C.validate_palette(["#000000", "#0000ff"], background="white")
        assert r.contrast_ok and r.passes
        r2 = C.validate_palette(["#ffff00", "#000000"], background="white")
        assert not r2.contrast_ok

    def test_to_dict_roundtrip_keys(self):
        d = C.validate_palette("deep").to_dict()
        assert {
            "n_colors",
            "min_delta_e",
            "closest_pair",
            "min_delta_e_cvd",
            "passes",
            "warnings",
        } <= set(d)

    def test_min_pairwise_single(self):
        d, pair = C.min_pairwise_distance(["red"])
        assert d == float("inf") and pair == (0, 0)


class TestCreatePalette:
    def test_default_qualitative(self):
        assert len(C.create_color_palette(n_colors=5)) == 5

    def test_custom(self):
        assert len(C.create_color_palette(colors=["red", "blue", "green"])) == 3

    @pytest.mark.parametrize("kind,n", [("sequential", 8), ("diverging", 11), ("qualitative", 8)])
    def test_types(self, kind, n):
        assert len(C.create_color_palette(palette_type=kind)) == n

    def test_bad_type(self):
        with pytest.raises(ValueError):
            C.create_color_palette(palette_type="rainbow")


class TestContrastOptOut:
    def test_check_contrast_false_ignores_contrast(self):
        strict = C.validate_palette("colorblind")
        lenient = C.validate_palette("colorblind", check_contrast=False)
        assert strict.distinguishable == lenient.distinguishable
        assert lenient.contrast_ok == strict.contrast_ok  # still measured
        assert not lenient.contrast_required
        assert lenient.passes == lenient.distinguishable
        assert not any("contrast" in w for w in lenient.warnings)

    def test_to_dict_reports_contrast_required(self):
        assert (
            C.validate_palette("deep", check_contrast=False).to_dict()["contrast_required"] is False
        )
