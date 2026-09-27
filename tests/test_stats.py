import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
from statsmodels.stats.multitest import multipletests

from seabornmasterpro import stats as S

pvals = arrays(np.float64, st.integers(1, 12), elements=st.floats(1e-6, 1.0))


class TestAdjustPvalues:
    @pytest.mark.parametrize("method", ["holm", "fdr_bh", "bonferroni"])
    @given(p=pvals)
    @settings(max_examples=60, deadline=None)
    def test_matches_statsmodels(self, method, p):
        ours = S.adjust_pvalues(p, method)
        ref = multipletests(p, method=method)[1]
        assert np.allclose(ours, ref)

    def test_none_is_identity(self):
        p = [0.1, 0.02]
        assert np.array_equal(S.adjust_pvalues(p, "none"), p)

    def test_empty(self):
        assert S.adjust_pvalues([], "holm").size == 0

    def test_bad_method(self):
        with pytest.raises(ValueError):
            S.adjust_pvalues([0.1], "sidak")  # type: ignore[arg-type]

    def test_adjusted_never_below_raw(self):
        p = np.array([0.01, 0.02, 0.5])
        for m in ("holm", "fdr_bh", "bonferroni"):
            assert np.all(S.adjust_pvalues(p, m) >= p - 1e-12)


class TestEffectSizes:
    def test_cohens_d_known_value(self):
        a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        b = np.array([3.0, 4.0, 5.0, 6.0, 7.0])
        # pooled sd = sqrt(2.5) so d = -2 / 1.5811 = -1.2649
        assert S.cohens_d(a, b) == pytest.approx(-1.2649, abs=1e-3)

    def test_hedges_g_smaller_than_d(self):
        rng = np.random.default_rng(0)
        a, b = rng.normal(0, 1, 15), rng.normal(1, 1, 15)
        assert abs(S.hedges_g(a, b)) < abs(S.cohens_d(a, b))

    def test_sign_convention(self, rng):
        a, b = rng.normal(0, 1, 100), rng.normal(2, 1, 100)
        assert S.cohens_d(a, b) < 0 < S.cohens_d(b, a)
        assert S.cliffs_delta(a, b) < 0 < S.cliffs_delta(b, a)

    def test_cliffs_delta_bounds_and_extremes(self):
        assert S.cliffs_delta([1, 2, 3], [10, 11, 12]) == pytest.approx(-1.0)
        assert S.cliffs_delta([10, 11, 12], [1, 2, 3]) == pytest.approx(1.0)
        assert -1 <= S.cliffs_delta([1, 5, 3, 4], [2, 3, 4, 5]) <= 1

    def test_identical_groups_zero(self):
        a = np.array([1.0, 2.0, 3.0])
        assert S.cohens_d(a, a) == 0.0
        assert S.cliffs_delta(a, a) == pytest.approx(0.0)

    def test_glass_delta_uses_control_sd(self):
        t = np.array([12.0, 14.0, 16.0])
        c = np.array([10.0, 11.0, 12.0])
        assert S.glass_delta(t, c) == pytest.approx((14 - 11) / 1.0)

    def test_nan_dropped(self):
        assert S.cohens_d([1, 2, np.nan, 3], [2, 3, 4]) == S.cohens_d([1, 2, 3], [2, 3, 4])

    def test_too_small(self):
        with pytest.raises(ValueError):
            S.cohens_d([1], [1, 2])

    @pytest.mark.parametrize(
        "v,label", [(0.1, "negligible"), (0.3, "small"), (0.6, "medium"), (1.2, "large")]
    )
    def test_interpret_d(self, v, label):
        assert S.interpret_effect_size(v) == label
        assert S.interpret_effect_size(-v) == label

    def test_interpret_delta(self):
        assert S.interpret_effect_size(0.2, "delta") == "small"
        assert S.interpret_effect_size(0.5, "delta") == "large"


class TestBootstrap:
    def test_deterministic_with_seed(self, rng):
        x = rng.normal(size=80)
        r1 = S.bootstrap_ci(x, seed=1, n_boot=300)
        r2 = S.bootstrap_ci(x, seed=1, n_boot=300)
        assert r1 == r2

    def test_interval_contains_estimate(self, rng):
        x = rng.normal(size=80)
        for method in ("percentile", "basic", "bca"):
            r = S.bootstrap_ci(x, method=method, n_boot=400)
            assert r.low <= r.estimate <= r.high
            assert r.method == method

    def test_coverage_roughly_nominal(self):
        rng = np.random.default_rng(7)
        hits = 0
        trials = 200
        for _ in range(trials):
            x = rng.normal(0, 1, 40)
            r = S.bootstrap_ci(x, n_boot=200, seed=rng)
            hits += r.low <= 0 <= r.high
        assert 0.88 <= hits / trials <= 0.99

    def test_custom_statistic(self, rng):
        x = rng.exponential(size=100)
        r = S.bootstrap_ci(x, np.median, n_boot=200)
        assert r.estimate == pytest.approx(np.median(x))

    def test_invalid(self):
        with pytest.raises(ValueError):
            S.bootstrap_ci([1.0])
        with pytest.raises(ValueError):
            S.bootstrap_ci([1.0, 2.0], confidence=1.5)
        with pytest.raises(ValueError):
            S.bootstrap_ci([1.0, 2.0, 3.0], method="magic")  # type: ignore[arg-type]


class TestPermutation:
    def test_detects_shift(self, rng):
        a, b = rng.normal(0, 1, 60), rng.normal(1.5, 1, 60)
        stat, p = S.permutation_test(a, b, n_permutations=999)
        assert stat < 0 and p < 0.01

    def test_null_not_tiny(self, rng):
        a, b = rng.normal(0, 1, 60), rng.normal(0, 1, 60)
        _, p = S.permutation_test(a, b, n_permutations=499)
        assert p > 0.01

    def test_p_never_zero_and_at_most_one(self, rng):
        a, b = rng.normal(0, 1, 10), rng.normal(50, 1, 10)
        _, p = S.permutation_test(a, b, n_permutations=99)
        assert 0 < p <= 1

    def test_one_sided(self, rng):
        a, b = rng.normal(1, 1, 60), rng.normal(0, 1, 60)
        _, p_greater = S.permutation_test(a, b, alternative="greater", n_permutations=499)
        _, p_less = S.permutation_test(a, b, alternative="less", n_permutations=499)
        assert p_greater < 0.05 < p_less


class TestCompareGroups:
    @pytest.mark.parametrize("test", ["welch", "student", "mannwhitney", "permutation"])
    def test_all_tests_run(self, three_groups, test):
        df = S.compare_groups(three_groups, "g", "y", test=test, n_permutations=200)
        assert len(df) == 3
        assert set(df["group_a"]) <= {"A", "B", "C"}
        assert (df["p_adjusted"] >= df["p_value"] - 1e-12).all()
        ac = df.loc[(df.group_a == "A") & (df.group_b == "C")].iloc[0]
        # With 200 permutations the smallest attainable p is 1/201, so only check significance.
        assert ac["p_adjusted"] < 0.05 and ac["stars"] != "ns"

    def test_effect_kind_by_test(self, three_groups):
        assert (S.compare_groups(three_groups, "g", "y")["effect_kind"] == "hedges_g").all()
        assert (
            S.compare_groups(three_groups, "g", "y", test="mannwhitney")["effect_kind"]
            == "cliffs_delta"
        ).all()

    def test_pairs_and_order(self, three_groups):
        df = S.compare_groups(three_groups, "g", "y", pairs=[("C", "A")], order=["C", "B", "A"])
        assert len(df) == 1 and df.iloc[0]["group_a"] == "C"
        assert df.iloc[0]["effect_size"] > 0

    def test_missing_column(self, three_groups):
        with pytest.raises(KeyError):
            S.compare_groups(three_groups, "nope", "y")

    def test_bad_test(self, three_groups):
        with pytest.raises(ValueError):
            S.compare_groups(three_groups, "g", "y", test="anova")  # type: ignore[arg-type]

    def test_group_summary(self, three_groups):
        s = S.group_summary(three_groups, "g", "y", n_boot=200)
        assert list(s["g"]) == ["A", "B", "C"]
        assert (s["low"] <= s["estimate"]).all() and (s["estimate"] <= s["high"]).all()
        assert (s["n"] == 50).all()


@pytest.mark.parametrize("p,stars", [(0.0001, "***"), (0.005, "**"), (0.04, "*"), (0.2, "ns")])
def test_p_to_stars(p, stars):
    assert S.p_to_stars(p) == stars


def test_dataframe_input_series(three_groups):
    r = S.bootstrap_ci(three_groups["y"], n_boot=100)
    assert isinstance(r, S.BootstrapResult)
    assert isinstance(pd.Series(three_groups["y"]), pd.Series)


class TestBootstrapSamples:
    def test_return_samples_shape_and_consistency(self, rng):
        x = rng.normal(size=40)
        r = S.bootstrap_ci(x, n_boot=500, seed=1, return_samples=True)
        assert r.samples is not None and r.samples.shape == (500,)
        lo, hi = np.percentile(r.samples, [2.5, 97.5])
        assert r.low == pytest.approx(lo) and r.high == pytest.approx(hi)

    def test_default_has_no_samples_and_to_dict_is_scalar(self, rng):
        r = S.bootstrap_ci(rng.normal(size=30), n_boot=200, seed=1)
        assert r.samples is None
        assert set(r.to_dict()) == {"estimate", "low", "high", "confidence", "n_boot", "method"}

    def test_group_summary_has_no_samples_column(self, three_groups):
        cols = S.group_summary(three_groups, "g", "y", n_boot=100).columns
        assert "samples" not in cols
